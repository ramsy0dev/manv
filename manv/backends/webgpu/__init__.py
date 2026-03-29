"""WebGPU backend entrypoints for ManV.

Emits WGSL (WebGPU Shading Language) from Kernel IR for execution
in WebGPU-capable environments (browsers, Dawn, wgpu).
"""

from __future__ import annotations

from .codegen import emit_wgsl

__all__ = ["emit_wgsl"]
