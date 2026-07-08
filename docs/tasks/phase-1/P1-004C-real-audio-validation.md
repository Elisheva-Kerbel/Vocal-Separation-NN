# P1-004C — Real Audio Validation

Status: **PLANNING STUB ONLY — NOT AUTHORIZED YET.**
Phase: 1 (AI Benchmark Harness) · Package: PKG-P1 · Depends on: P1-004B (adapter) passing review · Baseline: `stemspace-dev-pack-v0.1/tasks/phase-1/TASK-P1-004-real-audio-validation.md`

> **Planning stub only. Not authorized yet.**
> **Do not implement until Nadav review and an explicit prompt.**
> This file reserves the task and records intended future scope. It authorizes **no** inference and **no**
> real audio validation run.

## Expected future scope (not yet approved)

- A **real audio validation run**: exercise the (future, authorized) minimal local inference adapter on **one**
  real local audio file and collect evidence — vocals output, background output, metrics JSON, accepted
  `modelTier` — with **no checkpoint path supplied** in any output.
- Validation only: **no** code fixes, **no** model-choice changes, **no** upload/API integration.
- Audio fixtures stay **local / out-of-band**; **no** audio files are copied into the repo (per DEC-0004 Git policy).

## Not in this stub

- No inference run, no model loaded into memory, no benchmark executed.
- No audio / model / checkpoint files copied into the repo.
- No API / DB / queue / Redis / MinIO-S3 / frontend / worker integration.
- No production or commercial claim.

## Entry gate

Begins only after: P1-004B implemented and **passing review**, plus **Nadav review PASS** and an **explicit prompt**
authorizing P1-004C.

## Stop gate

Do not start. Wait for the P1-004B adapter to pass review and for explicit authorization.
