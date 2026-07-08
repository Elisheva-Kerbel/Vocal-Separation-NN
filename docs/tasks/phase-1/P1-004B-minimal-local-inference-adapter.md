# P1-004B — Minimal Local Inference Adapter

Status: **PLANNING STUB ONLY — NOT AUTHORIZED YET.**
Phase: 1 (AI Benchmark Harness) · Package: PKG-P1 · Depends on: `docs/decisions/DEC-0004-basic-local-model-prototype.md`, P1-004A

> **Planning stub only. Not authorized yet.**
> **Do not implement until Nadav review and an explicit prompt.**
> This file reserves the task and records intended future scope. It authorizes **no** code, dependency
> installation, model download, checkpoint copy, model loading or inference.

## Expected future scope (not yet approved)

- A **minimal local inference adapter** that, when later authorized, loads the approved **local out-of-band**
  Basic checkpoint (per DEC-0004) and performs a single local separation.
- Server-side wiring of the internal `use_best_model` selector (Basic slot may temporarily reuse the same
  checkpoint) — **never** exposing checkpoint paths to client / API / metrics.
- Prefer a **safe checkpoint-loading policy** (e.g. weights-only / restricted unpickling) given `.pt`
  pickle / deserialization risk.
- Expected dependencies (installed **only** when P1-004B is separately authorized): `torch`, `librosa`,
  `soundfile`, `numpy`, possibly `torchaudio`, and `ffmpeg` only if needed for input conversion.

## Not in this stub

- No implementation, no dependency installation, no model download, no checkpoint copy into the repo.
- No inference, no model loaded into memory.
- No API / DB / queue / Redis / MinIO-S3 / frontend / worker integration.
- No production or commercial claim; Professional remains not implemented.

## Entry gate

Begins only after: P1-004A accepted, **Nadav review PASS**, and an **explicit prompt** authorizing P1-004B.

## Stop gate

Do not start. Wait for review and explicit authorization.
