"""Idempotent seed for the P2-004 placeholder tags (DEC-0008 §2-§4).

Operator-invoked script only. Inserts EXACTLY the four DEC-0008 placeholder tags —
no product / user / song / job / audio / usage data. Idempotent by ``Tag.slug``:
running it again is a no-op for existing slugs (no duplicates, no error, no name
rewrite). It is **not** run on application or Docker Compose startup, is **not** an
Alembic data migration, targets **local** Compose Postgres only (never production),
and never logs or prints ``DATABASE_URL``, a password or any secret — only safe
summary counts.

Manual use (operator, against the local Compose database only):
    docker compose run --rm backend python -m scripts.seed_tags
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Tag

# DEC-0008 §2 — the exact, closed placeholder taxonomy: (slug, name). Placeholder
# only, NOT final product taxonomy, and implies no public-library behavior. No
# other tag may be seeded in P2-004.
SEED_TAGS: tuple[tuple[str, str], ...] = (
    ("vocals", "Vocals"),
    ("background", "Background"),
    ("instrumental", "Instrumental"),
    ("demo", "Demo"),
)


def seed_tags(session: Session) -> dict[str, int]:
    """Idempotently insert the approved placeholder tags into ``session``.

    Idempotent by ``slug`` via insert-if-absent (a lookup by slug, insert only when
    missing) — not by catching an ``IntegrityError`` as control flow, and it never
    rewrites an existing tag's ``name``. Commits once and returns safe count summary
    only (``created`` / ``skipped`` / ``total``) — never a URL, password or secret.
    """
    created = 0
    skipped = 0
    for slug, name in SEED_TAGS:
        already_present = session.scalar(select(Tag.id).where(Tag.slug == slug))
        if already_present is not None:
            skipped += 1
            continue
        session.add(Tag(slug=slug, name=name))
        created += 1
    session.commit()
    return {"created": created, "skipped": skipped, "total": len(SEED_TAGS)}


def format_summary(summary: dict[str, int]) -> str:
    """Render the safe, secret-free one-line summary printed by ``main``."""
    return (
        f"seed_tags: created={summary['created']} "
        f"skipped={summary['skipped']} total={summary['total']}"
    )


def main() -> None:
    """Operator entry point: seed against the configured local database.

    Uses the P2-001 session/config wiring (``app.db.get_sessionmaker`` →
    ``app.config.require_database_url``): it connects only when actually run, never
    at import and never on app/Compose startup, and fails clearly (without echoing
    the URL) when ``DATABASE_URL`` is unset. Prints safe counts only.
    """
    from app.db import get_sessionmaker

    with get_sessionmaker()() as session:
        summary = seed_tags(session)
    print(format_summary(summary))


if __name__ == "__main__":
    main()
