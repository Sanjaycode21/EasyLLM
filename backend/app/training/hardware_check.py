import os
import shutil
import subprocess
import psutil
from typing import Dict, Any

def get_hardware_status() -> Dict[str, Any]:
    """
    Returns real hardware and ML runtime diagnostic information.
    Inspects physical GPU (nvidia-smi), PyTorch CUDA status, VRAM, RAM, and installed libraries.
    """
    physical_gpu_name = None
    physical_vram_total_gb = 0.0
    physical_vram_free_gb = 0.0
    driver_version = None
    cuda_driver_version = None
    
    # 1. Inspect Physical GPU via nvidia-smi if available
    if shutil.which("nvidia-smi"):
        try:
            cmd = [
                "nvidia-smi",
                "--query-gpu=name,memory.total,memory.free,driver_version",
                "--format=csv,noheader,nounits"
            ]
            out = subprocess.check_output(cmd, encoding="utf-8", timeout=3).strip()
            if out:
                parts = [p.strip() for p in out.splitlines()[0].split(",")]
                if len(parts) >= 4:
                    physical_gpu_name = parts[0]
                    physical_vram_total_gb = round(float(parts[1]) / 1024, 2)
                    physical_vram_free_gb = round(float(parts[2]) / 1024, 2)
                    driver_version = parts[3]
        except Exception:
            pass

    # 2. Inspect PyTorch & PyTorch CUDA
    pytorch_version = "Not Installed"
    pytorch_cuda_available = False
    torch_device_count = 0
    torch_device_name = "CPU"
    torch_free_vram_gb = 0.0
    torch_total_vram_gb = 0.0

    try:
        import torch
        pytorch_version = torch.__version__
        pytorch_cuda_available = torch.cuda.is_available()
        if pytorch_cuda_available:
            torch_device_count = torch.cuda.device_count()
            torch_device_name = torch.cuda.get_device_name(0)
            mem_info = torch.cuda.mem_get_info()  # (free, total) bytes
            torch_free_vram_gb = round(mem_info[0] / (1024 ** 3), 2)
            torch_total_vram_gb = round(mem_info[1] / (1024 ** 3), 2)
    except Exception as e:
        pytorch_version = f"Error ({e})"

    # Prefer PyTorch device info if CUDA active, else physical GPU
    display_gpu = torch_device_name if pytorch_cuda_available else (physical_gpu_name or "CPU Only")
    total_vram = torch_total_vram_gb if pytorch_cuda_available else physical_vram_total_gb
    free_vram = torch_free_vram_gb if pytorch_cuda_available else physical_vram_free_gb

    # 3. Check ML Library Versions
    library_versions = {}
    for lib_name in ["transformers", "peft", "trl", "bitsandbytes", "accelerate", "datasets", "pymupdf", "sentence_transformers"]:
        try:
            mod = __import__(lib_name)
            library_versions[lib_name] = getattr(mod, "__version__", "Installed")
        except ImportError:
            library_versions[lib_name] = "Not Installed"

    # 4. CPU & RAM
    cpu_cores = os.cpu_count() or 1
    system_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    free_ram_gb = round(psutil.virtual_memory().available / (1024 ** 3), 2)

    # 5. Feasibility analysis for target model: Qwen/Qwen3-4B-Instruct-2507
    # 4-bit base weights: ~2.5 GB, Activations (seq_len=512, batch=1, LoRA r=8): ~1.5 GB => ~4.0 GB needed
    can_fit_qwen3_4b_local = pytorch_cuda_available and (free_vram >= 4.0)

    if can_fit_qwen3_4b_local:
        recommended_mode = "local_qlora_ready"
        recommended_mode_text = "Local GPU QLoRA Supported (Conservative 4-Bit)"
    elif pytorch_cuda_available and free_vram >= 2.0:
        recommended_mode = "local_rag_only"
        recommended_mode_text = "Local RAG Supported (Colab recommended for Qwen3-4B QLoRA)"
    elif physical_gpu_name:
        recommended_mode = "colab_recommended"
        recommended_mode_text = f"Hardware: {physical_gpu_name} ({total_vram}GB) · PyTorch CPU Mode active · Colab fallback for 4B QLoRA"
    else:
        recommended_mode = "cpu_only"
        recommended_mode_text = "CPU Mode Active · Colab Fallback for QLoRA Training"

    return {
        "gpu_name": display_gpu,
        "physical_gpu_name": physical_gpu_name or "N/A",
        "total_vram_gb": total_vram,
        "free_vram_gb": free_vram,
        "cuda_available": pytorch_cuda_available or bool(physical_gpu_name),
        "pytorch_cuda": pytorch_cuda_available,
        "pytorch_version": pytorch_version,
        "driver_version": driver_version,
        "cpu_cores": cpu_cores,
        "system_ram_gb": system_ram_gb,
        "free_ram_gb": free_ram_gb,
        "libraries": library_versions,
        "target_model": "Qwen/Qwen3-4B-Instruct-2507",
        "can_fit_qwen3_4b_local": can_fit_qwen3_4b_local,
        "recommended_mode": recommended_mode,
        "recommended_mode_text": recommended_mode_text,
    }
