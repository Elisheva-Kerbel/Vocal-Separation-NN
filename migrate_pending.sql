-- Pending migration: run inside postgres container
-- docker compose exec postgres psql -U stemspace -d stemspace -f /dev/stdin < migrate_pending.sql

-- 1. Add subscription_expires_at column (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'subscription_expires_at'
    ) THEN
        ALTER TABLE users ADD COLUMN subscription_expires_at TIMESTAMPTZ;
    END IF;
END $$;

-- 2. Drop profile_visibility column and constraint (if exists)
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'profile_visibility_allowed' AND table_name = 'users'
    ) THEN
        ALTER TABLE users DROP CONSTRAINT profile_visibility_allowed;
    END IF;
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'profile_visibility'
    ) THEN
        ALTER TABLE users DROP COLUMN profile_visibility;
    END IF;
END $$;

-- 3. Create coupon for upgrading
INSERT INTO coupons (id, code, tier_grant, days_valid, max_redemptions, active)
VALUES (gen_random_uuid(), 'VOCALSPLIT-PRO', 'pro', 365, 100, true)
ON CONFLICT (code) DO NOTHING;

-- Verify
SELECT column_name FROM information_schema.columns WHERE table_name = 'users' ORDER BY ordinal_position;
SELECT id, code, days_valid, max_redemptions, active FROM coupons;
