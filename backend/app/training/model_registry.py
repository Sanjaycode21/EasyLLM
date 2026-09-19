from typing import List, Dict, Any, Optional

SUPPORTED_MODELS: List[Dict[str, Any]] = [
    {
        "model_id": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "display_name": "SmolLM2 135M Instruct (Ultra Fast & Lightweight)",
        "parameters": "135M",
        "context_length": 2048,
        "minimum_vram_gb": 1.0,
        "supports_cpu_training": True,
        "supports_qlora": True,
        "recommended_for": ["Low-resource compute", "Fast experimentation", "Simple Q&A", "Customer support"],
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    },
    {
        "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "display_name": "Qwen 2.5 0.5B Instruct (Balanced Accuracy)",
        "parameters": "500M",
        "context_length": 4096,
        "minimum_vram_gb": 2.5,
        "supports_cpu_training": True,
        "supports_qlora": True,
        "recommended_for": ["Domain knowledge", "Formatting adherence", "Multi-turn dialog"],
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    },
    {
        "model_id": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
        "display_name": "TinyLlama 1.1B Chat (Conversational)",
        "parameters": "1.1B",
        "context_length": 2048,
        "minimum_vram_gb": 4.0,
        "supports_cpu_training": False,
        "supports_qlora": True,
        "recommended_for": ["Stylistic chat", "Persona customization"],
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    }
]

def get_model_config(model_id: str) -> Optional[Dict[str, Any]]:
    for m in SUPPORTED_MODELS:
        if m["model_id"] == model_id:
            return m
    # Return generic fallback config
    return {
        "model_id": model_id,
        "display_name": model_id.split("/")[-1],
        "parameters": "Unknown",
        "context_length": 2048,
        "minimum_vram_gb": 4.0,
        "supports_cpu_training": True,
        "supports_qlora": True,
        "recommended_for": ["Custom instruct"],
        "target_modules": ["q_proj", "v_proj"],
    }

def select_optimal_model(cuda_available: bool, free_vram_gb: float) -> str:
    """
    Selects the optimal model based on available hardware.
    Never downloads or picks models that the host machine cannot realistically run.
    """
    if not cuda_available:
        return "HuggingFaceTB/SmolLM2-135M-Instruct"
    
    if free_vram_gb >= 6.0:
        return "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
    elif free_vram_gb >= 2.5:
        return "Qwen/Qwen2.5-0.5B-Instruct"
    else:
        return "HuggingFaceTB/SmolLM2-135M-Instruct"
