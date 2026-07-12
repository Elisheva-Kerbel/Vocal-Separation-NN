"""P1-004B local prototype model architecture tests.

Prove the minimal re-implemented separation architecture:

- imports with NO torch (torch is lazy — asserted via a subprocess);
- exposes the audio front-end constants matching the local reference;
- when torch IS available, builds a single-mask U-Net whose layer layout matches
  the reference (so an approved checkpoint can be loaded later) and whose forward
  pass returns a same-sized single-channel mask in [0, 1].

No checkpoint is loaded and no weights are bundled: build_model() returns an
untrained network. The torch-dependent tests skip cleanly when torch is absent.
"""

import subprocess
import sys

import ai.local_model as lm


def test_module_imports_without_torch():
    # Importing the architecture module must not pull torch into sys.modules.
    code = (
        "import sys, ai.local_model\n"
        "sys.exit(1 if 'torch' in sys.modules else 0)\n"
    )
    result = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
    assert result.returncode == 0, "importing ai.local_model must not import torch"


def test_audio_frontend_constants_match_reference():
    assert lm.SAMPLE_RATE == 22050
    assert lm.N_FFT == 1024
    assert lm.HOP_LENGTH == 256
    # Single-channel magnitude in, single-channel vocals mask out.
    assert lm.INPUT_CHANNELS == 1
    assert lm.MASK_CHANNELS == 1


def test_build_model_returns_expected_layers():
    # Architecture check: the submodule names must match the reference so a saved
    # state_dict loads later. Requires torch; skips cleanly otherwise.
    import pytest

    torch = pytest.importorskip("torch")
    model = lm.build_model()
    assert isinstance(model, torch.nn.Module)
    children = set(dict(model.named_children()))
    assert children == {"enc1", "enc2", "pool", "bottleneck", "dec2", "dec1", "out_conv"}


def test_forward_produces_same_size_single_channel_mask_in_unit_range():
    import pytest

    torch = pytest.importorskip("torch")
    model = lm.build_model().eval()
    x = torch.randn(1, 1, 64, 48)  # [B, 1, freq, time]
    with torch.no_grad():
        mask = model(x)
    assert mask.shape == x.shape  # same spatial size, single channel
    assert float(mask.min()) >= 0.0 and float(mask.max()) <= 1.0
