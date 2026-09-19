import os
import psutil
from typing import Dict, Any

def get_hardware_status() -> Dict[str, Any]:
    """
    Returns real hardware diagnostic information.
    Inspects CUDA, GPU VRAM, CPU cores, and system memory.
    """
    cuda_available = False
    device_name = "CPU"
    device_count = 0
    total_vram_gb = 0.0
    free_vram_gb = 0.0
    
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_count = torch.cuda.device_count()
            device_name = torch.cuda.get_device_name(0)
            mem_info = torch.cuda.mem_get_info() # (free, total) in bytes
            free_vram_gb = round(mem_info[0] / (1024 ** 3), 2)
            total_vram_gb = round(mem_info[1] / (1024 ** 3), 2)
    except Exception as e:
        device_name = f"CPU (Torch load note: {str(e)})"

    cpu_cores = os.cpu_count() or 1
    system_ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 2)
    
    # Recommendation logic
    if cuda_available and total_vram_gb >= 12:
        recommended_quant = "4bit"
    elif cuda_available and total_vram_gb >= 6:
        recommended_quant = "4bit"
    elif cuda_available:
        recommended_quant = "8bit"
    else:
        recommended_quant = "cpu_fp32"

    return {
        "cuda_available": cuda_available,
        "device_name": device_name,
        "device_count": device_count,
        "total_vram_gb": total_vram_gb,
        "free_vram_gb": free_vram_gb,
        "cpu_cores": cpu_cores,
        "system_ram_gb": system_ram_gb,
        "recommended_quantization": recommended_quant,
    }
