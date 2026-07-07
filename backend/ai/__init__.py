"""StemSpace AI package — Phase 1 (TASK-P1-001) module boundaries only.

This package defines the *boundaries* for the AI benchmark harness: the model
vocabulary, the inference entry point, audio I/O, the metrics shape and the
server-side checkpoint registry. Nothing here does real work yet:

- no model is loaded, downloaded or executed;
- no audio is decoded or encoded;
- no network, filesystem-audio, DB, queue, Redis or S3/MinIO access;
- no third-party AI/audio dependencies are imported.

Real inference, the checkpoint tier mapping and the benchmark CLI arrive in the
later, separately approved Phase 1 tasks (P1-002 / P1-003 / P1-004). Only
**Vocals + Background** stems are ever in scope (02-product-scope-and-do-not-build).
"""
