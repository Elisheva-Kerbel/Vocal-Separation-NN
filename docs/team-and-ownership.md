# Team and Phase Ownership

Status: **Draft — pending Nadav readiness review.**

This project is built by a two-person team. Commit attribution follows **phase ownership**:
each phase is owned by one teammate, and **all commits for that phase are authored and
committed under that teammate's identity** (attribution is per phase / area of responsibility,
not alternated commit-by-commit).

## Contributors

| Name             | Git name         | Email                    |
|------------------|------------------|--------------------------|
| Elisheva Kerbel  | `Elisheva-Kerbel`| `ch355739@gmail.com`     |
| Brachi Lubling   | `Brachi-Lubling` | `brachil5119@gmail.com`  |

> **GitHub credit note:** for the contribution graph to credit each teammate, her email above
> must be added to her own GitHub account (Settings → Emails). The commit author/committer is
> set correctly regardless, but GitHub links a commit to an account by verified email.

## Phase ownership (split by subsystem, balanced 7 / 6)

| Phase | Title                                   | Owner    |
|-------|-----------------------------------------|----------|
| 0     | Dockerized project skeleton             | Elisheva |
| 1     | AI benchmark harness                    | Elisheva |
| 2     | Backend domain + DB skeleton            | Brachi   |
| 3     | Auth / user account foundation          | Elisheva |
| 4     | Upload + private storage                | Elisheva |
| 5     | Queue + worker processing               | Brachi   |
| 6     | Result page + secure file access        | Brachi   |
| 7     | Quotas + coupons                        | Elisheva |
| 8     | My library                              | Elisheva |
| 9     | Public library                          | Brachi   |
| 10    | Admin RBAC + audit                      | Brachi   |
| 11    | Settings + account deletion             | Brachi   |
| 12    | QA hardening + release readiness        | Elisheva |

- **Elisheva (7):** 0, 1, 3, 4, 7, 8, 12 — foundation, AI, auth, upload, business & release.
- **Brachi (6):** 2, 5, 6, 9, 10, 11 — backend/DB, processing, secure access, sharing/admin/account.

Areas of responsibility: Elisheva owns the foundation, AI, auth, upload and
user-content/business tracks; Brachi owns the backend domain/DB, processing and
security/access/admin tracks.

## How to commit under the right identity

Set author **and** committer per commit so both match the phase owner:

```bash
# Elisheva's phases
git -c user.name="Elisheva-Kerbel" -c user.email="ch355739@gmail.com" commit -F <msgfile>

# Brachi's phases
git -c user.name="Brachi-Lubling"  -c user.email="brachil5119@gmail.com" commit -F <msgfile>
```

Convenience aliases (configured locally in `.git/config`, not tracked):

```bash
git ce   # commit as Elisheva
git cb   # commit as Brachi
```

## Rules

- Commit messages are attributed **only** to Elisheva or Brachi (no other co-author trailers).
- One phase → one owner. Do not mix owners within a phase's commits.
- Follow `git-workflow.md` for commit cadence, size and message style.
- This mapping may be adjusted by the team; update this table if ownership changes.
