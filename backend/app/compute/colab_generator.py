import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from app.api.schemas import BuildConfiguration

class ColabNotebookGenerator:
    """
    Generates genuine, executable Jupyter/Google Colab notebooks (.ipynb)
    tailored specifically for Qwen3-4B-Instruct-2507 4-bit QLoRA fine-tuning.
    """
    @staticmethod
    def generate_notebook(
        config: BuildConfiguration,
        training_records: List[Dict[str, Any]],
        job_id: str
    ) -> Dict[str, Any]:
        dataset_json_str = json.dumps(training_records, indent=2)
        base_model = config.base_model_id or "Qwen/Qwen3-4B-Instruct-2507"
        epochs = config.epochs or 2
        lora_rank = config.lora_rank or 8
        lora_alpha = config.lora_alpha or 16
        lr = config.learning_rate or 2e-4
        max_seq_len = config.max_seq_length or 512

        notebook = {
            "nbformat": 4,
            "nbformat_minor": 0,
            "metadata": {
                "accelerator": "GPU",
                "colab": {
                    "name": f"EasyLLM_Qwen3_4B_QLoRA_{job_id[:8]}.ipynb",
                    "provenance": []
                },
                "kernelspec": {
                    "display_name": "Python 3",
                    "name": "python3"
                },
                "language_info": {
                    "name": "python"
                }
            },
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        f"# 🚀 EasyLLM: Qwen3-4B-Instruct-2507 QLoRA Training Pipeline\n",
                        f"**Job ID:** `{job_id}`  \n",
                        f"**Target Model:** `{base_model}`  \n",
                        f"**Architecture:** QLoRA 4-bit NormalFloat (NF4) with Rank $r={lora_rank}$, Alpha $\\alpha={lora_alpha}$  \n",
                        f"**Optimized Settings:** Sequence Length={max_seq_len}, Batch Size=1, Gradient Accumulation=4, Gradient Checkpointing=Enabled.\n\n",
                        "This notebook was autonomously configured by **EasyLLM** to train your customized AI on Google Colab (Free T4 / A100 GPU)."
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 1. Install Real Deep Learning & QLoRA Dependencies\n",
                        "!pip install -q torch transformers peft trl bitsandbytes datasets accelerate\n",
                        "!nvidia-smi"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "import torch\n",
                        "import json\n",
                        "from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, TrainingArguments\n",
                        "from peft import LoraConfig, get_peft_model, TaskType, prepare_model_for_kbit_training\n",
                        "from trl import SFTTrainer\n",
                        "from datasets import Dataset\n\n",
                        f"MODEL_ID = '{base_model}'\n",
                        "print('CUDA Available:', torch.cuda.is_available())\n",
                        "if torch.cuda.is_available():\n",
                        "    print('GPU Device:', torch.cuda.get_device_name(0))\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 2. Ingest Dataset (Pre-injected from your EasyLLM job)\n",
                        f"RAW_RECORDS = {dataset_json_str}\n\n",
                        "formatted_texts = []\n",
                        "for r in RAW_RECORDS:\n",
                        "    msgs = r.get('messages', [])\n",
                        "    turn_text = []\n",
                        "    for m in msgs:\n",
                        "        role = m.get('role', 'user')\n",
                        "        content = m.get('content', '')\n",
                        "        turn_text.append(f'<|im_start|>{role}\\n{content}<|im_end|>')\n",
                        "    formatted_texts.append('\\n'.join(turn_text))\n\n",
                        "dataset = Dataset.from_dict({'text': formatted_texts})\n",
                        "print(f'Successfully loaded {len(dataset)} training sequences for Qwen3.')\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 3. Load Qwen3-4B Base Model in 4-bit Quantization\n",
                        "bnb_config = BitsAndBytesConfig(\n",
                        "    load_in_4bit=True,\n",
                        "    bnb_4bit_quant_type='nf4',\n",
                        "    bnb_4bit_use_double_quant=True,\n",
                        "    bnb_4bit_compute_dtype=torch.float16\n",
                        ")\n\n",
                        "tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)\n",
                        "if tokenizer.pad_token is None:\n",
                        "    tokenizer.pad_token = tokenizer.eos_token\n\n",
                        "model = AutoModelForCausalLM.from_pretrained(\n",
                        "    MODEL_ID,\n",
                        "    quantization_config=bnb_config,\n",
                        "    device_map='auto',\n",
                        "    trust_remote_code=True\n",
                        ")\n",
                        "model = prepare_model_for_kbit_training(model)\n",
                        "model.gradient_checkpointing_enable()\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 4. Apply Parameter-Efficient LoRA Adapters\n",
                        f"lora_config = LoraConfig(\n",
                        f"    r={lora_rank},\n",
                        f"    lora_alpha={lora_alpha},\n",
                        f"    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],\n",
                        f"    lora_dropout=0.05,\n",
                        f"    bias='none',\n",
                        f"    task_type=TaskType.CAUSAL_LM\n",
                        f")\n\n",
                        "peft_model = get_peft_model(model, lora_config)\n",
                        "peft_model.print_trainable_parameters()\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 5. Execute Supervised Fine-Tuning (SFT)\n",
                        f"training_args = TrainingArguments(\n",
                        f"    output_dir='./easyllm_qwen3_output',\n",
                        f"    num_train_epochs={epochs},\n",
                        f"    per_device_train_batch_size=1,\n",
                        f"    gradient_accumulation_steps=4,\n",
                        f"    gradient_checkpointing=True,\n",
                        f"    learning_rate={lr},\n",
                        f"    fp16=True,\n",
                        f"    logging_steps=1,\n",
                        f"    save_strategy='no',\n",
                        f"    report_to='none'\n",
                        f")\n\n",
                        f"trainer = SFTTrainer(\n",
                        f"    model=peft_model,\n",
                        f"    train_dataset=dataset,\n",
                        f"    dataset_text_field='text',\n",
                        f"    max_seq_length={max_seq_len},\n",
                        f"    tokenizer=tokenizer,\n",
                        f"    args=training_args\n",
                        f")\n\n",
                        "print('Starting Qwen3 QLoRA fine-tuning...')\n",
                        "trainer.train()\n"
                    ]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "execution_count": None,
                    "outputs": [],
                    "source": [
                        "# 6. Export Trained LoRA Adapter Package for EasyLLM\n",
                        "ADAPTER_DIR = './easyllm_adapter'\n",
                        "trainer.model.save_pretrained(ADAPTER_DIR)\n",
                        "tokenizer.save_pretrained(ADAPTER_DIR)\n\n",
                        "!zip -r easyllm_qwen3_adapter.zip ./easyllm_adapter\n",
                        "from google.colab import files\n",
                        "files.download('easyllm_qwen3_adapter.zip')\n",
                        "print('🎉 Training complete! Upload easyllm_qwen3_adapter.zip back into EasyLLM.')\n"
                    ]
                }
            ]
        }
        return notebook

    @staticmethod
    def save_notebook(
        config: BuildConfiguration,
        training_records: List[Dict[str, Any]],
        job_id: str,
        output_path: Path
    ) -> Path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        nb_data = ColabNotebookGenerator.generate_notebook(config, training_records, job_id)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(nb_data, f, indent=2)
        return output_path
