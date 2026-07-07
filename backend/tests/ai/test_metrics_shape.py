"""P1-003 benchmark metrics schema tests.

Prove the metrics JSON contract the benchmark CLI writes: every required key is
present (including the nested ``output_sizes`` for the two in-scope stems and the
checkpoint cold/warm-start fields), timing/size values may be null, populated
values map correctly, the writer persists valid JSON into a created directory,
and no metric value leaks an internal checkpoint reference, path, storage key,
URL or secret.
"""

import json

from ai.metrics import METRICS_FILENAME, BenchmarkMetrics, write_metrics

# The metric keys the phase/task require in the JSON contract.
REQUIRED_TOP_LEVEL_KEYS = {
    "success",
    "failure_reason",
    "modelTier",
    "total_runtime",
    "decode_time",
    "inference_time",
    "encode_time",
    "output_sizes",
    "checkpoint_cold_start",
    "checkpoint_warm_start",
}

# Substrings that would betray a leaked path / filename / URL / storage key /
# internal checkpoint reference / secret in any string value.
_LEAK_MARKERS = (
    "/",
    "\\",
    "..",
    "~",
    ":",
    "http",
    "s3",
    "minio",
    "placeholder",
    "secret",
    ".pt",
    ".pth",
    ".ckpt",
    ".onnx",
    ".bin",
    ".safetensors",
)


def _string_values(obj):
    """Yield every string value nested anywhere in ``obj`` (keys excluded)."""
    if isinstance(obj, dict):
        for value in obj.values():
            yield from _string_values(value)
    elif isinstance(obj, (list, tuple)):
        for value in obj:
            yield from _string_values(value)
    elif isinstance(obj, str):
        yield obj


def test_default_metrics_have_all_required_keys():
    data = BenchmarkMetrics().to_dict()
    assert REQUIRED_TOP_LEVEL_KEYS <= set(data)


def test_output_sizes_shape():
    # output_sizes exists and nests exactly the two in-scope stems.
    data = BenchmarkMetrics().to_dict()
    assert set(data["output_sizes"]) == {"vocals", "background"}


def test_default_failure_shape_values():
    # A default (unrun) metrics object is a structured failure with null timings.
    data = BenchmarkMetrics().to_dict()
    assert data["success"] is False
    assert data["failure_reason"] is None
    assert data["modelTier"] is None
    for key in (
        "total_runtime",
        "decode_time",
        "inference_time",
        "encode_time",
        "checkpoint_cold_start",
        "checkpoint_warm_start",
    ):
        assert data[key] is None
    assert data["output_sizes"]["vocals"] is None
    assert data["output_sizes"]["background"] is None


def test_populated_metrics_map_to_contract():
    # Every dataclass field maps to its required JSON contract key/name.
    metrics = BenchmarkMetrics(
        success=True,
        failure_reason=None,
        model_tier="Basic",
        runtime_seconds=1.0,
        decode_seconds=0.1,
        inference_seconds=0.7,
        encode_seconds=0.2,
        vocals_bytes=11,
        background_bytes=22,
        checkpoint_cold_start_seconds=0.5,
        checkpoint_warm_start_seconds=0.05,
    )
    data = metrics.to_dict()
    assert data["success"] is True
    assert data["modelTier"] == "Basic"
    assert data["total_runtime"] == 1.0
    assert data["decode_time"] == 0.1
    assert data["inference_time"] == 0.7
    assert data["encode_time"] == 0.2
    assert data["output_sizes"] == {"vocals": 11, "background": 22}
    assert data["checkpoint_cold_start"] == 0.5
    assert data["checkpoint_warm_start"] == 0.05


def test_output_sizes_allow_zero_on_failure():
    # output_sizes may legitimately carry 0 (or null) values on failure.
    data = BenchmarkMetrics(vocals_bytes=0, background_bytes=0).to_dict()
    assert data["output_sizes"] == {"vocals": 0, "background": 0}


def test_write_metrics_creates_dir_and_valid_json(tmp_path):
    # The writer creates a missing (nested) output directory and writes valid,
    # re-parseable JSON containing the full contract.
    target = tmp_path / "nested" / "out"
    path = write_metrics(BenchmarkMetrics(model_tier="Professional"), str(target))
    assert path.endswith(METRICS_FILENAME)
    written = target / METRICS_FILENAME
    assert written.is_file()
    data = json.loads(written.read_text(encoding="utf-8"))
    assert REQUIRED_TOP_LEVEL_KEYS <= set(data)
    assert data["modelTier"] == "Professional"


def test_metrics_json_values_have_no_leak_markers(tmp_path):
    # Even a fully-populated, valid metrics object must contain no path / URL /
    # storage key / internal checkpoint ref / secret marker in any string value.
    metrics = BenchmarkMetrics(
        success=True,
        failure_reason=None,
        model_tier="Professional",
        runtime_seconds=1.0,
        decode_seconds=0.1,
        inference_seconds=0.7,
        encode_seconds=0.2,
        vocals_bytes=1,
        background_bytes=2,
    )
    path = write_metrics(metrics, str(tmp_path))
    data = json.loads(open(path, encoding="utf-8").read())
    for value in _string_values(data):
        lowered = value.lower()
        for marker in _LEAK_MARKERS:
            assert marker not in lowered, f"metrics value leaks {marker!r}: {value!r}"
