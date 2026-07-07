"""P1-002 checkpoint registry tests.

Prove the server-side modelTier -> internal reference mapping: Basic and
Professional resolve to opaque internal references; only those two tiers are
accepted; path/filename/URL/storage-like and empty/non-string inputs are
rejected with safe errors; and no client-facing result leaks an internal
reference, path, storage key, URL or checkpoint filename.
"""

import inspect

import pytest

import ai.checkpoint_registry as registry
from ai.model import ModelTier

# Substrings that would betray a leaked path / filename / URL / storage key in an
# internal reference or a client-facing value.
_LEAK_MARKERS = (
    "/",
    "\\",
    "..",
    "~",
    ":",
    "http",
    "s3",
    "minio",
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".bin",
    ".safetensors",
)


def test_basic_resolves_to_internal_entry():
    assert registry.resolve_checkpoint("Basic") == "basic-placeholder"


def test_professional_resolves_to_internal_entry():
    assert registry.resolve_checkpoint("Professional") == "professional-placeholder"


def test_enum_members_resolve():
    # Internal callers may pass the ModelTier enum member directly.
    assert registry.resolve_checkpoint(ModelTier.BASIC) == "basic-placeholder"
    assert (
        registry.resolve_checkpoint(ModelTier.PROFESSIONAL)
        == "professional-placeholder"
    )


def test_only_basic_and_professional_tiers_exist():
    assert {tier.value for tier in ModelTier} == {"Basic", "Professional"}
    assert len(ModelTier) == 2


@pytest.mark.parametrize(
    "tier",
    [
        "Free",
        "Pro",
        "Premium",
        "Enterprise",
        "Admin",
        "Experimental",
        "Custom",
        # Strict, no normalization: wrong case / padding is not accepted.
        "basic",
        "professional",
        "BASIC",
        " Basic ",
    ],
)
def test_unknown_tiers_are_rejected(tier):
    with pytest.raises(ValueError):
        registry.resolve_checkpoint(tier)


@pytest.mark.parametrize(
    "raw",
    [
        "/models/vocals.pt",
        "..\\checkpoints\\model.ckpt",
        "backend/ai/checkpoints/model.safetensors",
        "C:\\models\\demucs.pth",
        "~/secret_checkpoint.bin",
    ],
)
def test_path_like_values_are_rejected(raw):
    with pytest.raises(ValueError):
        registry.resolve_checkpoint(raw)


@pytest.mark.parametrize(
    "raw",
    ["model.onnx", "checkpoint.pt", "weights.safetensors", "demucs.ckpt", "model.bin"],
)
def test_filename_like_values_are_rejected(raw):
    with pytest.raises(ValueError):
        registry.resolve_checkpoint(raw)


@pytest.mark.parametrize(
    "raw",
    [
        "http://example.com/model.pt",
        "https://example.com/model",
        "s3://bucket/key",
        "s3:bucket",
        "minio://x/y",
    ],
)
def test_url_and_storage_like_values_are_rejected(raw):
    with pytest.raises(ValueError):
        registry.resolve_checkpoint(raw)


@pytest.mark.parametrize(
    "raw",
    ["", "   ", None, 123, 4.5, b"Basic", ["Basic"], ModelTier],
)
def test_empty_and_non_string_values_are_rejected(raw):
    with pytest.raises(ValueError):
        registry.resolve_checkpoint(raw)


def test_invalid_tier_error_is_safe():
    with pytest.raises(ValueError) as exc:
        registry.resolve_checkpoint("Premium")
    msg = str(exc.value)
    # Lists the safe accepted tiers...
    assert "Basic" in msg and "Professional" in msg
    # ...and leaks no internal reference.
    assert "placeholder" not in msg.lower()


def test_path_rejection_error_is_safe():
    with pytest.raises(ValueError) as exc:
        registry.resolve_checkpoint("/models/secret.pt")
    msg = str(exc.value)
    # No internal reference and no echoed input path/secret.
    assert "placeholder" not in msg.lower()
    assert "/models/secret.pt" not in msg


def test_internal_reference_is_opaque_not_a_path():
    for tier in ModelTier:
        ref = registry.resolve_checkpoint(tier).lower()
        for marker in _LEAK_MARKERS:
            assert marker not in ref, f"internal ref looks like a path/URL/key: {ref!r}"


def test_public_response_hides_internal_reference():
    for tier in ModelTier:
        internal = registry.resolve_checkpoint(tier)
        public = registry.public_checkpoint_response(tier)
        # The client-facing view echoes only the logical tier label...
        assert public == {"modelTier": tier.value}
        # ...never the internal reference or any path/URL/key/filename.
        assert internal not in public.values()
        for value in public.values():
            lowered = value.lower()
            for marker in _LEAK_MARKERS:
                assert marker not in lowered


@pytest.mark.parametrize(
    "func", [registry.resolve_checkpoint, registry.public_checkpoint_response]
)
def test_boundary_functions_take_only_model_tier(func):
    # No client-style boundary accepts a raw checkpoint path/filename/id parameter.
    params = inspect.signature(func).parameters
    assert set(params) == {"model_tier"}
    for name in params:
        assert "path" not in name
        assert "checkpoint" not in name
        assert "file" not in name
