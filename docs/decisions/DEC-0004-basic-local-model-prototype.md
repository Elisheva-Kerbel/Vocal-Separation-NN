# DEC-0004 — Basic local model prototype only

Status: **Approved for local prototype / technical validation only.**
Not production-approved. Not commercially approved. Professional tier is **not implemented**.
Supersedes the Basic side of open decision **OD-004** (real checkpoint choice) **for local prototype use only**; the Professional side of OD-004 remains open.

Phase: 1 (AI Benchmark Harness) · Package: PKG-P1 · Relates to: P1-002 (checkpoint registry / `modelTier`), P1-004 (real audio validation)

> This record documents an **approved planning decision** for a local Basic prototype. It authorizes **no** implementation by itself. Runtime code, dependency installation, model download, checkpoint copying and inference remain **out of scope** until P1-004B is separately reviewed and explicitly authorized (see §10).

## 1. Decision

Use a **Basic local model prototype only**. The locally available, self-trained separation checkpoint may be wired in later as the **Basic** slot for a local proof-of-concept / technical validation. This is a prototype decision, not a product-tier decision.

## 2. Status

**Approved for local prototype / technical validation only.** No production approval, no public users, no commercial-use approval. Approval covers *planning and future local wiring*, not the actions this record explicitly defers.

## 3. Approved checkpoint source

- **Local out-of-band folder only.** The checkpoint lives outside the repository, in the operator's local model folder, and is referenced out-of-band.
- Approved candidate checkpoint (local only), shown as a neutral placeholder:
  `<LOCAL_MODEL_ROOT>/checkpoints/best_model.pt`
- The **real checkpoint path is local / out-of-band only** and is intentionally **not recorded here**. It must be **provided by the operator during local prototype setup** (e.g. via a local, uncommitted `.env` / config value that resolves `<LOCAL_MODEL_ROOT>`).
- The **real path must not be committed to Git**, and **checkpoint / model weights must not be committed to Git** (see §4).
- The folder was inspected **read-only**. Nothing is copied into the repository.
- This path is an **internal / operator-side** reference only. It must never be exposed to client, API responses or metrics, and must not appear in user-facing output (see §9).

## 4. Git policy

- Checkpoint / model weights **must not be committed to Git — now or in the future.**
- No `.pt` / `.pth` / `.ckpt` / `.safetensors` / `.onnx` / `.bin` (or equivalent weight) files, and no audio fixtures, enter the repository.
- Any future adapter must read weights from the **local out-of-band folder**, never from a repo-tracked copy.

## 5. Tier behavior

- A future implementation **may** use an internal boolean selector `use_best_model` (backend/server-side only):
  - `use_best_model = true` → routes to `best_model.pt`.
  - `use_best_model = false` → routes to the **basic checkpoint slot**.
- For now, the **basic checkpoint slot may temporarily point to the same checkpoint** as `best_model.pt`.
- This selector is an **internal detail**. It is not a client input and not a client-visible value; it does not change the existing rule that a client sends only a logical `modelTier` and never a checkpoint path, filename or id (P1-002).
- **This is not a Professional tier.** The temporary reuse of one checkpoint must **not** be presented as a real Professional tier to anyone.
- **Professional remains not implemented / blocked** until a separate, production-grade checkpoint is approved in its own decision. The existing `professional-placeholder` registry entry stays an opaque placeholder.

## 6. Scope

In scope (planning / future local use):

- Basic demo / proof-of-concept only.
- Local prototype / technical validation only.

Explicitly **out of scope**:

- No production approval.
- No public users.
- No commercial-use approval.
- No upload / queue / DB / API / Redis / MinIO-S3 / frontend / worker integration.
- No claim that Professional is implemented.

## 7. Licensing / provenance

- The local model **appears to be self-trained**.
- Training data, license and provenance **still need resolution before production**.
- The current checkpoint is **not production-approved**.
- Production requires **licensing / provenance clearance** or a **replacement production-approved model**.
- Until then, use is confined to local prototype / technical validation as described here.

## 8. Dependencies expected for future implementation

Expected (for a *future* adapter, **not** approved for installation in P1-004A and **not** installed by this record):

- `torch`
- `librosa`
- `soundfile`
- `numpy`
- possibly `torchaudio`
- `ffmpeg` only if needed for input conversion / preprocessing

These are documented for planning only. No dependency is added to `requirements.txt` and nothing is installed under this decision.

## 9. Security notes

- Loading a `.pt` checkpoint carries **pickle / deserialization risk** (arbitrary code execution on load).
- A future adapter must prefer a **safe loading policy** where possible (e.g. `weights_only` loading / restricted unpickling, or a safer serialization format).
- **Do not load untrusted checkpoints.** Only the vetted local out-of-band checkpoint is in scope.
- **Do not expose checkpoint paths** to client, API or metrics.
- **Do not print checkpoint paths in user-facing output.**

## 10. Next task sequencing

- **P1-004A** — this decision record only. *(Currently authorized.)*
- **P1-004B** — minimal local inference adapter implementation. **Only after review** and an explicit prompt.
- **P1-004C** — real audio validation run. **Only after** the P1-004B adapter is implemented and passes review.

## Rationale

The project needs a concrete, low-risk path to prove local separation end-to-end without prematurely committing to a production model, installing dependencies, or copying weights into the repo. Scoping the local self-trained checkpoint to a Basic prototype — behind a server-side selector, with licensing/provenance and production approval explicitly deferred — preserves every downstream boundary (private storage DEC-0003, minimal code DEC-0002, no path leakage P1-002) while unblocking local technical validation planning.
