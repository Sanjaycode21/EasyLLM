from typing import List, Dict, Any, Optional

SUPPORTED_MODELS: List[Dict[str, Any]] = [
    {
        "model_id": "Qwen/Qwen3-4B-Instruct-2507",
        "display_name": "Qwen 3 4B Instruct 2507 (Primary Target Foundation Model)",
        "parameters": "4.0B",
        "context_length": 32768,
        "recommended_context_length_6gb": 512,
        "minimum_vram_gb": 4.5,
        "recommended_vram_gb": 6.0,
        "supports_cpu_training": False,
        "supports_qlora": True,
        "load_in_4bit": True,
        "conservative_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "gradient_checkpointing": True,
        "recommended_for": [
            "High-accuracy instruction following",
            "Complex enterprise workflows",
            "Multi-turn conversational personas",
            "Domain-specific formatting & syntax"
        ],
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        "prompt_template": {
            "system_prefix": "<|im_start|>system\n",
            "system_suffix": "<|im_end|>\n",
            "user_prefix": "<|im_start|>user\n",
            "user_suffix": "<|im_end|>\n",
            "assistant_prefix": "<|im_start|>assistant\n",
            "assistant_suffix": "<|im_end|>"
        }
    },
    {
        "model_id": "Qwen/Qwen2.5-0.5B-Instruct",
        "display_name": "Qwen 2.5 0.5B Instruct (Lightweight Edge & CPU Testing)",
        "parameters": "500M",
        "context_length": 4096,
        "recommended_context_length_6gb": 1024,
        "minimum_vram_gb": 2.0,
        "recommended_vram_gb": 3.0,
        "supports_cpu_training": True,
        "supports_qlora": True,
        "load_in_4bit": True,
        "conservative_batch_size": 1,
        "gradient_accumulation_steps": 2,
        "gradient_checkpointing": True,
        "recommended_for": ["Fast local CPU testing", "Lightweight chat"],
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    },
    {
        "model_id": "HuggingFaceTB/SmolLM2-135M-Instruct",
        "display_name": "SmolLM2 135M Instruct (Ultra Fast Local Prototype)",
        "parameters": "135M",
        "context_length": 2048,
        "recommended_context_length_6gb": 1024,
        "minimum_vram_gb": 1.0,
        "recommended_vram_gb": 1.5,
        "supports_cpu_training": True,
        "supports_qlora": True,
        "load_in_4bit": False,
        "conservative_batch_size": 2,
        "gradient_accumulation_steps": 2,
        "gradient_checkpointing": False,
        "recommended_for": ["Instant 20-second RAG pairing", "Lightweight local prototyping"],
        "target_modules": ["q_proj", "v_proj", "k_proj", "o_proj"],
    }
]

def get_model_config(model_id: str) -> Dict[str, Any]:
    for m in SUPPORTED_MODELS:
        if m["model_id"] == model_id:
            return m
    # Return sensible default for Qwen / Causal LM family
    return {
        "model_id": model_id,
        "display_name": model_id.split("/")[-1],
        "parameters": "4.0B",
        "context_length": 2048,
        "recommended_context_length_6gb": 512,
        "minimum_vram_gb": 4.5,
        "supports_cpu_training": False,
        "supports_qlora": True,
        "load_in_4bit": True,
        "conservative_batch_size": 1,
        "gradient_accumulation_steps": 4,
        "gradient_checkpointing": True,
        "recommended_for": ["Custom instruct"],
        "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj"],
    }

def select_optimal_model(cuda_available: bool, free_vram_gb: float) -> str:
    """
    Selects the optimal base model.
    Defaults to Qwen/Qwen3-4B-Instruct-2507 as the primary target architecture.
    """
    return "Qwen/Qwen3-4B-Instruct-2507"

def compute_automatic_training_params(model_id: str, free_vram_gb: float, dataset_size: int) -> Dict[str, Any]:
    """
    Automatically calculates optimal hyperparameters for 6GB VRAM constraint.
    The user never needs to configure batch size, sequence length, or LoRA rank manually.
    """
    cfg = get_model_config(model_id)
    
    # 1. Conservative Sequence Length (prevents OOM on 6GB RTX 3050)
    if free_vram_gb >= 12.0:
        max_seq_len = 1024
    elif free_vram_gb >= 5.0:
        max_seq_len = 512
    else:
        max_seq_len = 256

    # 2. Batch size & gradient accumulation
    batch_size = 1
    grad_accum = 4 if dataset_size > 10 else 2
    
    # 3. LoRA Configuration (Rank 8, Alpha 16 is robust and lightweight)
    lora_rank = 8
    lora_alpha = 16
    lr = 2e-4

    return {
        "base_model_id": model_id,
        "max_seq_length": max_seq_len,
        "per_device_batch_size": batch_size,
        "gradient_accumulation_steps": grad_accum,
        "gradient_checkpointing": True,
        "load_in_4bit": True,
        "lora_rank": lora_rank,
        "lora_alpha": lora_alpha,
        "learning_rate": lr,
        "epochs": 2 if dataset_size < 50 else 1,
    }
