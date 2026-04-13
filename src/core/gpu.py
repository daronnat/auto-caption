"""GPU detection and VRAM monitoring for all major hardware vendors."""

import platform

# Estimated VRAM requirements for known models (in MB)
MODEL_VRAM_ESTIMATES = {
    "Qwen/Qwen3.5-0.8B": 1700,
}


def detect_gpu() -> dict:
    """Detect available GPU hardware. Returns info dict with device, name, VRAM, etc."""
    info = {
        "device": "cpu",
        "device_name": "CPU",
        "vram_total_mb": 0,
        "vram_free_mb": 0,
        "backend_hint": "cpu",
    }

    try:
        import torch
    except ImportError:
        return info

    # NVIDIA CUDA or AMD ROCm (both use torch.cuda API)
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        props = torch.cuda.get_device_properties(0)
        total_mb = props.total_mem // (1024 * 1024)
        reserved_mb = torch.cuda.memory_reserved(0) // (1024 * 1024)

        is_rocm = hasattr(torch.version, "hip") and torch.version.hip is not None

        info.update({
            "device": "cuda",
            "device_name": f"{'AMD' if is_rocm else 'NVIDIA'} {device_name}",
            "vram_total_mb": total_mb,
            "vram_free_mb": total_mb - reserved_mb,
            "backend_hint": "rocm" if is_rocm else "cuda",
        })
        return info

    # Apple Silicon MPS
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        info.update({
            "device": "mps",
            "device_name": "Apple Silicon (MPS)",
            "vram_total_mb": _get_macos_unified_memory_mb(),
            "vram_free_mb": 0,
            "backend_hint": "mps",
        })
        return info

    # Intel XPU (Arc / Data Center GPUs via intel-extension-for-pytorch)
    if hasattr(torch, "xpu") and torch.xpu.is_available():
        try:
            device_name = torch.xpu.get_device_name(0)
        except Exception:
            device_name = "Unknown"
        info.update({
            "device": "xpu",
            "device_name": f"Intel {device_name}",
            "vram_total_mb": 0,
            "vram_free_mb": 0,
            "backend_hint": "xpu",
        })
        return info

    return info


def get_vram_usage() -> tuple[int, int]:
    """Return (used_mb, total_mb). Returns (0, 0) if unavailable."""
    try:
        import torch
        if torch.cuda.is_available():
            used = torch.cuda.memory_reserved(0) // (1024 * 1024)
            total = torch.cuda.get_device_properties(0).total_mem // (1024 * 1024)
            return used, total
    except (ImportError, RuntimeError):
        pass
    return 0, 0


def check_vram_sufficient(model_id: str, gpu_info: dict) -> tuple[bool, str]:
    """Check if GPU has enough VRAM for a model. Returns (ok, warning_message)."""
    estimated_mb = MODEL_VRAM_ESTIMATES.get(model_id, 0)
    if estimated_mb == 0:
        return True, ""

    total_mb = gpu_info.get("vram_total_mb", 0)
    if total_mb == 0:
        return True, ""

    if estimated_mb > total_mb:
        return False, f"~{estimated_mb} MB needed, {total_mb} MB available"

    if estimated_mb > total_mb * 0.8:
        return True, f"~{estimated_mb} MB needed, {total_mb} MB available (tight)"

    return True, ""


def _get_macos_unified_memory_mb() -> int:
    """Get total system memory on macOS (unified memory for Apple Silicon)."""
    if platform.system() != "Darwin":
        return 0
    try:
        import subprocess
        output = subprocess.check_output(
            ["sysctl", "-n", "hw.memsize"], text=True
        ).strip()
        return int(output) // (1024 * 1024)
    except Exception:
        return 0
