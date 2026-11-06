"""
GPU hardware detection and backend availability reporting.

This module provides a unified interface for detecting available GPU
accelerators (CUDA, JAX, CuPy, PyTorch) and reporting their status.
It does NOT provide GPU-accelerated simulation kernels — those are
handled by MesoHOPS/SBD natively on CPU.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)


@dataclass
class GpuInfo:
    available: bool = False
    backend: Optional[str] = None
    device_count: int = 0
    device_names: List[str] = field(default_factory=list)
    cuda_version: Optional[str] = None
    driver_version: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


def detect_gpu() -> GpuInfo:
    """Probe all known GPU backends and return a consolidated status report."""
    info = GpuInfo()
    _check_nvidia_smi(info)
    _check_jax(info)
    _check_cupy(info)
    _check_pytorch(info)
    return info


def _check_nvidia_smi(info: GpuInfo) -> None:
    """Query nvidia-smi for CUDA driver and device info."""
    import shutil
    import subprocess

    if not shutil.which("nvidia-smi"):
        return
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            info.warnings.append(f"nvidia-smi failed: {result.stderr.strip()}")
            return
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) >= 1:
                info.device_names.append(parts[0])
            if len(parts) >= 2 and info.driver_version is None:
                info.driver_version = parts[1]
        info.device_count = len(info.device_names)
        if info.device_count > 0:
            info.available = True
    except FileNotFoundError:
        pass


def _check_jax(info: GpuInfo) -> None:
    """Check if JAX can see GPU devices."""
    try:
        import jax

        devices = jax.devices("gpu")
        if devices:
            info.available = True
            info.backend = "jax"
            if info.device_count == 0:
                info.device_count = len(devices)
                info.device_names = [str(d) for d in devices]
    except Exception:
        pass


def _check_cupy(info: GpuInfo) -> None:
    """Check if CuPy is available and can see GPUs."""
    try:
        import cupy as cp

        n = cp.cuda.runtime.getDeviceCount()
        if n > 0:
            info.available = True
            info.backend = "cupy"
            if info.device_count == 0:
                info.device_count = n
                for i in range(n):
                    info.device_names.append(
                        cp.cuda.runtime.getDeviceProperties(i)["name"].decode()
                    )
    except Exception:
        pass


def _check_pytorch(info: GpuInfo) -> None:
    """Check if PyTorch CUDA is available."""
    try:
        import torch

        if torch.cuda.is_available():
            info.available = True
            info.backend = info.backend or "pytorch"
            n = torch.cuda.device_count()
            if info.device_count == 0:
                info.device_count = n
                for i in range(n):
                    info.device_names.append(torch.cuda.get_device_name(i))
    except Exception:
        pass


def log_gpu_status(info: Optional[GpuInfo] = None) -> GpuInfo:
    """Detect GPU hardware and log a human-readable status report."""
    if info is None:
        info = detect_gpu()
    if info.available:
        logger.info(
            f"GPU detected: backend={info.backend}, count={info.device_count}, "
            f"devices={info.device_names}"
        )
    else:
        logger.info("No GPU detected — running on CPU (recommended for MesoHOPS).")
    for w in info.warnings:
        logger.warning(f"GPU warning: {w}")
    return info
