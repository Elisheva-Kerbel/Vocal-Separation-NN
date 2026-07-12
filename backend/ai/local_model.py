"""Minimal local prototype separation architecture (P1-004B).

Re-implements — from a **read-only** inspection of the local reference project —
the small U-Net that predicts a vocals mask from a magnitude spectrogram, so the
approved local checkpoint can be loaded *later* (P1-004C). Nothing from the local
model folder is imported, executed or copied; this is an independent, minimal
re-implementation kept isolated in the ``ai`` package.

``torch`` is imported **lazily** inside :func:`build_model` (never at module top),
so importing this module needs no torch and pulls in no heavy library — the AI
boundary stays import-light (see ``tests/ai/test_imports.py``). No checkpoint is
loaded here and no weights are bundled: :func:`build_model` returns an *untrained*
network whose weights are random until a checkpoint is loaded later.

Local prototype only (DEC-0004): Basic demo / technical validation. Not
production-approved; not a Professional tier.
"""

from __future__ import annotations

# Audio front-end constants, matching the inspected local reference so a
# later-loaded checkpoint sees the same feature shapes. Plain values — importing
# this module pulls in no numpy/librosa/torch.
SAMPLE_RATE = 22050
N_FFT = 1024
HOP_LENGTH = 256

# The network input is a single-channel magnitude spectrogram and its output is a
# single-channel vocals mask in [0, 1]; Background is derived from that mask
# (1 - mask) downstream. Only Vocals + Background ever exist.
INPUT_CHANNELS = 1
MASK_CHANNELS = 1


def _import_torch():
    """Import torch lazily; raise a safe, path-free error if it is unavailable."""
    try:
        import torch
        import torch.nn as nn
        import torch.nn.functional as F
    except ImportError as exc:  # pragma: no cover - environment dependent
        raise RuntimeError(
            "PyTorch is required to build the local prototype model but is not "
            "installed in this environment."
        ) from exc
    return torch, nn, F


def build_model():
    """Build an untrained ``SmallUNet`` instance (torch imported lazily).

    Architecture only — returns a ``torch.nn.Module`` with **random** weights. No
    checkpoint is loaded and no local file is read here; the module's ``state_dict``
    layout mirrors the reference so an approved checkpoint can be loaded later
    (P1-004C). The layer names (``enc1``/``enc2``/``bottleneck``/``dec2``/``dec1``/
    ``out_conv``) must stay in sync with that checkpoint.
    """
    torch, nn, F = _import_torch()

    def conv_block(in_ch: int, out_ch: int):
        # Two 3x3 Conv2d + ReLU; padding=1 keeps the spatial size unchanged.
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
        )

    class SmallUNet(nn.Module):
        """Small U-Net (channels 16/32/64) predicting a vocals mask in [0, 1]."""

        def __init__(self) -> None:
            super().__init__()
            # Encoder
            self.enc1 = conv_block(INPUT_CHANNELS, 16)
            self.enc2 = conv_block(16, 32)
            self.pool = nn.MaxPool2d(kernel_size=2)
            # Bottleneck
            self.bottleneck = conv_block(32, 64)
            # Decoder (channels = upsampled + skip)
            self.dec2 = conv_block(64 + 32, 32)
            self.dec1 = conv_block(32 + 16, 16)
            # Final 1x1 conv to a single mask channel
            self.out_conv = nn.Conv2d(16, MASK_CHANNELS, kernel_size=1)

        def _up_to(self, x, skip):
            # Upsample x to skip's spatial size (spectrograms are often odd), then
            # concatenate on the channel dimension.
            x = F.interpolate(x, size=skip.shape[-2:], mode="nearest")
            return torch.cat([x, skip], dim=1)

        def forward(self, x):
            input_size = x.shape[-2:]
            e1 = self.enc1(x)
            e2 = self.enc2(self.pool(e1))
            b = self.bottleneck(self.pool(e2))
            d2 = self.dec2(self._up_to(b, e2))
            d1 = self.dec1(self._up_to(d2, e1))
            mask = torch.sigmoid(self.out_conv(d1))
            if mask.shape[-2:] != input_size:
                mask = F.interpolate(mask, size=input_size, mode="nearest")
            return mask

    return SmallUNet()
