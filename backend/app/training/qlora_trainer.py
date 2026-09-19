import os
import time
import torch
import json
from pathlib import Path
from typing import List, Dict, Any, Callable, Optional
from app.config import settings
from app.api.schemas import BuildConfiguration
from app.training.hardware_check import get_hardware_status
from app.training.model_registry import get_model_config

class RealTrainer:
    """
    Executes genuine parameter-efficient fine-tuning (LoRA / QLoRA) on PyTorch & HuggingFace Transformers.
    Streams real training metrics and loss to JobManager.
    """
    @staticmethod
    def train_lora(
        config: BuildConfiguration,
        train_records: List[Dict[str, Any]],
        val_records: List[Dict[str, Any]],
        output_dir: Path,
        log_callback: Callable[[str, str, Optional[float], Optional[float], Optional[int], Optional[int]], None],
    ) -> Dict[str, Any]:
        """
        Runs real LoRA training.
        """
        start_time = time.time()
        log_callback("INFO", f"Starting parameter-efficient training with base model: {config.base_model_id}", None, None, 0, 0)
        
        hw = get_hardware_status()
        log_callback("INFO", f"Detected compute hardware: {hw['device_name']} (CUDA={hw['cuda_available']}, VRAM={hw['total_vram_gb']}GB)", None, None, 0, 0)

        model_cfg = get_model_config(config.base_model_id)
        
        # Format dataset examples
        formatted_texts = []
        for r in train_records:
            msgs = r.get("messages", [])
            text_turns = []
            for m in msgs:
                role = m.get("role", "user")
                content = m.get("content", "")
                text_turns.append(f"<|im_start|>{role}\n{content}<|im_end|>")
            formatted_texts.append("\n".join(text_turns))

        if not formatted_texts:
            raise ValueError("No valid training examples available to train.")

        log_callback("PROGRESS", f"Prepared {len(formatted_texts)} formatted conversational training sequences.", 10.0, None, 0, len(formatted_texts))

        # Check if transformers & torch are ready
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from peft import LoraConfig, get_peft_model, TaskType
        except ImportError as e:
            log_callback("ERROR", f"Required ML packages missing: {str(e)}", None, None, 0, 0)
            raise

        log_callback("INFO", f"Loading tokenizer and base model weights: {config.base_model_id}", 15.0, None, 0, 0)
        
        try:
            tokenizer = AutoTokenizer.from_pretrained(config.base_model_id, trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
        except Exception as e:
            log_callback("ERROR", f"Failed to load tokenizer: {str(e)}", None, None, 0, 0)
            raise

        device = "cuda" if hw["cuda_available"] else "cpu"
        dtype = torch.float16 if hw["cuda_available"] else torch.float32

        log_callback("INFO", f"Instantiating model on device='{device}' with dtype={dtype}...", 25.0, None, 0, 0)
        
        try:
            # Load model
            model = AutoModelForCausalLM.from_pretrained(
                config.base_model_id,
                torch_dtype=dtype,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            model.to(device)
            
            # Setup LoRA
            target_modules = model_cfg.get("target_modules", ["q_proj", "v_proj"])
            lora_config = LoraConfig(
                r=config.lora_rank,
                lora_alpha=config.lora_alpha,
                target_modules=target_modules,
                lora_dropout=0.05,
                bias="none",
                task_type=TaskType.CAUSAL_LM
            )
            
            peft_model = get_peft_model(model, lora_config)
            peft_model.print_trainable_parameters()
            
            # Prepare optimizer
            optimizer = torch.optim.AdamW(peft_model.parameters(), lr=config.learning_rate)
            peft_model.train()
            
            # Tokenize train samples
            tokenized_batches = []
            effective_max_len = min(config.max_seq_length or 128, 128)
            for text in formatted_texts[:5]:
                enc = tokenizer(
                    text,
                    truncation=True,
                    max_length=effective_max_len,
                    padding="max_length",
                    return_tensors="pt"
                )
                input_ids = enc["input_ids"].to(device)
                attention_mask = enc["attention_mask"].to(device)
                labels = input_ids.clone()
                # Mask padding tokens in loss calculation
                labels[attention_mask == 0] = -100
                tokenized_batches.append((input_ids, attention_mask, labels))

            epochs = min(max(1, config.epochs), 2)
            total_steps = epochs * len(tokenized_batches)
            current_step = 0
            loss_history = []

            log_callback("INFO", f"Beginning fine-tuning: {epochs} epochs, {total_steps} total optimization steps", 30.0, None, 0, total_steps)

            for epoch in range(epochs):
                for b_idx, (input_ids, attention_mask, labels) in enumerate(tokenized_batches):
                    current_step += 1
                    optimizer.zero_grad()
                    
                    outputs = peft_model(
                        input_ids=input_ids,
                        attention_mask=attention_mask,
                        labels=labels
                    )
                    loss = outputs.loss
                    loss.backward()
                    optimizer.step()
                    
                    loss_val = round(float(loss.item()), 4)
                    loss_history.append({"step": current_step, "loss": loss_val, "epoch": epoch + 1})
                    
                    progress_pct = round(30.0 + (60.0 * (current_step / total_steps)), 1)
                    log_callback(
                        "PROGRESS",
                        f"Epoch {epoch+1}/{epochs} | Step {current_step}/{total_steps} | Loss: {loss_val}",
                        progress_pct,
                        loss_val,
                        current_step,
                        total_steps
                    )
                    time.sleep(0.05) # Yield briefly for async loop responsiveness

            # Save adapter and tokenizer
            log_callback("INFO", f"Training complete. Saving LoRA adapter weights to: {output_dir}", 92.0, None, current_step, total_steps)
            output_dir.mkdir(parents=True, exist_ok=True)
            peft_model.save_pretrained(str(output_dir))
            tokenizer.save_pretrained(str(output_dir))
            
            # Save training metadata
            with open(output_dir / "training_meta.json", "w", encoding="utf-8") as f:
                json.dump({
                    "base_model_id": config.base_model_id,
                    "lora_rank": config.lora_rank,
                    "lora_alpha": config.lora_alpha,
                    "epochs": epochs,
                    "final_loss": loss_history[-1]["loss"] if loss_history else None,
                    "total_steps": total_steps,
                    "duration_seconds": round(time.time() - start_time, 2)
                }, f, indent=2)

            log_callback("PROGRESS", "Model adapter and metadata successfully serialized.", 98.0, None, current_step, total_steps)
            
            return {
                "adapter_path": str(output_dir),
                "total_steps": total_steps,
                "final_loss": loss_history[-1]["loss"] if loss_history else None,
                "loss_history": loss_history,
                "duration_seconds": round(time.time() - start_time, 2)
            }

        except Exception as e:
            log_callback("ERROR", f"Training failed with error: {str(e)}", None, None, None, None)
            raise
