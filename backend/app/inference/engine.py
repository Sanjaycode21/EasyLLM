import time
import torch
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.config import settings
from app.rag.vector_store import VectorStore
from app.api.schemas import RetrievedSource, ChatResponse
from app.architect.llm_provider import get_llm_provider

class InferenceEngine:
    """
    Unified Inference Runtime for RAG, Fine-Tuned LoRA Models, and Hybrid systems.
    Executes actual forward passes, vector lookups, and latency profiling.
    """
    _loaded_models: Dict[str, Any] = {} # Cache for loaded models/tokenizers

    @classmethod
    def load_peft_model_and_tokenizer(cls, adapter_path: Path, base_model_id: str):
        key = str(adapter_path)
        if key in cls._loaded_models:
            return cls._loaded_models[key]
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            from peft import PeftModel
            
            tokenizer = AutoTokenizer.from_pretrained(str(adapter_path), trust_remote_code=True)
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
                
            base_model = AutoModelForCausalLM.from_pretrained(
                base_model_id,
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True,
                trust_remote_code=True
            )
            peft_model = PeftModel.from_pretrained(base_model, str(adapter_path))
            peft_model.eval()
            
            cls._loaded_models[key] = (peft_model, tokenizer)
            return peft_model, tokenizer
        except Exception as e:
            print(f"[InferenceEngine] Warning: Could not load local PEFT model ({e}).")
            return None, None

    @classmethod
    async def generate_response(
        cls,
        model_id: str,
        message: str,
        model_info: Dict[str, Any],
        history: Optional[List[Dict[str, str]]] = None
    ) -> ChatResponse:
        start_time = time.time()
        architecture = model_info.get("architecture", "rag")
        base_model_id = model_info.get("base_model", settings.default_base_model)
        adapter_path_str = model_info.get("adapter_path")
        sources_used: List[RetrievedSource] = []

        # 1. Handle RAG or Hybrid Knowledge Retrieval
        context_text = ""
        if architecture in ["rag", "hybrid"]:
            vector_store = VectorStore.load(model_id)
            if len(vector_store.chunks) > 0:
                retrieval_results = vector_store.search(message, top_k=3)
                for chunk, score in retrieval_results:
                    meta = chunk.get("metadata", {})
                    sources_used.append(RetrievedSource(
                        document_name=meta.get("document_name", "knowledge_base"),
                        page=meta.get("page"),
                        chunk_index=meta.get("chunk_index", 0),
                        snippet=chunk.get("text", "")[:250] + "...",
                        relevance_score=round(score, 3)
                    ))
                context_text = "\n\n".join([f"[Source: {c.get('metadata', {}).get('document_name', '')}]\n{c.get('text', '')}" for c, _ in retrieval_results])

        # 2. Construct Prompt
        system_prompt = (
            "You are a helpful, professional AI assistant built by EasyLLM."
        )
        if context_text:
            system_prompt += (
                f"\n\nUse the following verified reference context to accurately answer the user question:\n"
                f"--- REFERENCE CONTEXT ---\n{context_text}\n--- END CONTEXT ---\n"
                f"Base your answer strictly on the facts provided in the reference context."
            )

        # 3. Model Generation (Try local PEFT model first if adapter exists)
        generated_text = ""
        used_local_weights = False
        
        chat_history_str = ""
        history_text = ""
        if history:
            for turn in history:
                role = turn.get("role", "user")
                content = turn.get("content", "")
                chat_history_str += f"<|im_start|>{role}\n{content}<|im_end|>\n"
                if role == "user":
                    history_text += f"\nUser: {content}"
                else:
                    history_text += f"\nAssistant: {content}"

        if adapter_path_str and Path(adapter_path_str).exists():
            peft_model, tokenizer = cls.load_peft_model_and_tokenizer(Path(adapter_path_str), base_model_id)
            if peft_model and tokenizer:
                try:
                    prompt_formatted = f"<|im_start|>system\n{system_prompt}<|im_end|>\n{chat_history_str}<|im_start|>user\n{message}<|im_end|>\n<|im_start|>assistant\n"
                    inputs = tokenizer(prompt_formatted, return_tensors="pt")
                    with torch.no_grad():
                        outputs = peft_model.generate(
                            **inputs,
                            max_new_tokens=256,
                            temperature=0.3,
                            do_sample=True,
                            pad_token_id=tokenizer.pad_token_id
                        )
                    # Decode only new tokens
                    new_tokens = outputs[0][inputs["input_ids"].shape[1]:]
                    generated_text = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
                    used_local_weights = True
                except Exception as e:
                    print(f"[InferenceEngine] PEFT generation failed: {e}")

        if not generated_text:
            # Generate using LLMProvider with grounded context
            provider = get_llm_provider()
            full_prompt = f"{system_prompt}\n{history_text}\n\nUser Question: {message}"
            generated_text = await provider.generate_text(full_prompt)

        latency_ms = round((time.time() - start_time) * 1000, 1)

        return ChatResponse(
            message=generated_text,
            model_id=model_id,
            architecture=architecture,
            sources=sources_used if sources_used else None,
            metadata={
                "latency_ms": latency_ms,
                "base_model": base_model_id,
                "used_trained_adapter": used_local_weights,
                "num_sources_retrieved": len(sources_used)
            }
        )
