# FAST-DEMO-005 — End-to-End Demo Evidence

Status: **PLANNING STUB — NOT AUTHORIZED YET. Requires an explicit Nadav prompt. Do not implement yet.**
Track: FAST-DEMO (local demo vertical slice) · Package: none
Depends on: **FAST-DEMO-003 and FAST-DEMO-004 complete and accepted** ·
**`docs/decisions/DEC-0009-local-demo-vertical-slice.md`** (the contract for this task)
Relates to: `DEC-0004` §4 (Git policy), `docs/tasks/phase-1/P1-004C-real-audio-validation.md` (evidence
precedent), `stemspace-dev-pack-v0.1/templates/evidence-report-template.md`

> **Do not implement yet.** This document is a planning stub. It records *what this task will be* so the
> work can start mechanically when authorized — it authorizes **nothing** on its own. No run and no
> commit may happen until Nadav issues an explicit FAST-DEMO-005 prompt, and not before FAST-DEMO-003
> and FAST-DEMO-004 are accepted.

## Goal

Run the complete local demo once, end to end, in a browser, and record the **outcome** — with no audio,
no path and no metric values entering the repository.

## What to do (when authorized)

1. Start the local stack with the read-only `/models` mount in place (FAST-DEMO-002 configuration).
2. In the browser: open the frontend, select a local audio file, trigger Basic separation, and confirm
   the result screen renders both stems.
3. Verify **playback** of Vocals and Background, and that both **download links** work.
4. Exercise at least one **safe failure** path (e.g. an over-cap file) and confirm the error state shows
   a safe message with no path, checkpoint reference or internal detail.
5. Re-run the full regression set: backend suite, worker startup check, frontend build.
6. Record the outcome in this document, following the P1-004C precedent.

## Evidence policy (binding)

- Evidence is retained **out-of-band**. This document records the **outcome only**.
- **No** audio file (input or output), **no** checkpoint and **no** model file enters Git
  (`DEC-0004` §4 — permanent).
- **No** local host path, machine path, `LOCAL_MODEL_ROOT` value or checkpoint filename is written into
  this document or any committed file.
- **No** metric values, filenames or screenshots containing paths are reproduced here.
- Screenshots, if taken, stay out-of-band; if any were ever shown, they must contain no path, no
  filesystem chrome and no secret.

## What NOT to do

- Do not commit audio, model, checkpoint or output files.
- Do not add code, routes, UI or dependencies — this task is a **validation run**, like P1-004C. If a
  defect is found, **report it**; fixing it is a separate authorized task.
- Do not claim production readiness, commercial approval, public-user readiness or a Professional tier
  on the basis of this run.
- Do not touch the Dev Pack.

## Required checks

1. `docker compose run --rm --no-deps backend python -m pytest -q` — green.
2. `docker compose run --rm --no-deps worker python -m app.worker --check` — exit 0.
3. `docker compose run --rm --no-deps frontend npm run build` — passes.
4. `git status --short` — docs-only; no audio/model/checkpoint artifact anywhere in the repo.

## Evidence to return

Outcome (pass/fail) · checks run · manual verification (upload, both stems play, both downloads work,
safe-failure path) · known gaps · deviations · blockers · confirmation that no path, audio, checkpoint or
secret was committed.

## Stop gate

Stop after this task. The demo track ends here. Any further work — hardening, persistence, auth, real
storage, queue — requires its own decision and authorization; the DEC-0009 §3 deviations expire with the
demo and may not be reused as precedent.
