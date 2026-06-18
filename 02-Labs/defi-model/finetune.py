#!/usr/bin/env python3
"""
GenTech DeFi Model — QLoRA Fine-Tuning Script
Fine-tunes DeepSeek R1 Distill 32B on DeFi training data
"""

import json
from pathlib import Path
from datetime import datetime

# Configuration
MODEL_NAME = "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B"
TRAINING_DATA_PATH = Path("/root/vaults/gentech/02-Labs/defi-model/final-training-20260618.jsonl")
OUTPUT_PATH = Path("/root/vaults/gentech/02-Labs/defi-model/model")

# QLoRA Config
QLORA_CONFIG = {
    "r": 16,  # LoRA rank
    "lora_alpha": 32,  # LoRA alpha
    "lora_dropout": 0.05,  # LoRA dropout
    "target_modules": ["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    "bias": "none",
    "task_type": "CAUSAL_LM"
}

# Training Config
TRAINING_CONFIG = {
    "num_train_epochs": 3,
    "per_device_train_batch_size": 2,
    "gradient_accumulation_steps": 8,
    "learning_rate": 2e-4,
    "weight_decay": 0.01,
    "warmup_steps": 100,
    "logging_steps": 10,
    "save_steps": 100,
    "output_dir": str(OUTPUT_PATH),
    "fp16": True,
    "optim": "paged_adamw_32bit",
    "lr_scheduler_type": "cosine",
    "max_grad_norm": 0.3,
    "max_steps": -1,
    "group_by_length": True,
    "report_to": "none"
}

def create_training_script():
    """Create the fine-tuning script"""
    script = f'''#!/usr/bin/env python3
"""
GenTech DeFi Model — QLoRA Fine-Tuning
Run this on BlockRun Modal with GPU
"""

import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training
)
from trl import SFTTrainer

# Load dataset
dataset = load_dataset("json", data_files="{TRAINING_DATA_PATH}", split="train")

# Quantization config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True
)

# Load model
model = AutoModelForCausalLM.from_pretrained(
    "{MODEL_NAME}",
    quantization_config=bnb_config,
    device_map="auto",
    trust_remote_code=True
)

# Load tokenizer
tokenizer = AutoTokenizer.from_pretrained("{MODEL_NAME}", trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token

# Prepare model for training
model = prepare_model_for_kbit_training(model)

# LoRA config
lora_config = LoraConfig(
    r={QLORA_CONFIG["r"]},
    lora_alpha={QLORA_CONFIG["lora_alpha"]},
    lora_dropout={QLORA_CONFIG["lora_dropout"]},
    target_modules={QLORA_CONFIG["target_modules"]},
    bias="{QLORA_CONFIG["bias"]}",
    task_type="{QLORA_CONFIG["task_type"]}"
)

# Apply LoRA
model = get_peft_model(model, lora_config)

# Training arguments
training_args = TrainingArguments(
    output_dir="{TRAINING_CONFIG["output_dir"]}",
    num_train_epochs={TRAINING_CONFIG["num_train_epochs"]},
    per_device_train_batch_size={TRAINING_CONFIG["per_device_train_batch_size"]},
    gradient_accumulation_steps={TRAINING_CONFIG["gradient_accumulation_steps"]},
    learning_rate={TRAINING_CONFIG["learning_rate"]},
    weight_decay={TRAINING_CONFIG["weight_decay"]},
    warmup_steps={TRAINING_CONFIG["warmup_steps"]},
    logging_steps={TRAINING_CONFIG["logging_steps"]},
    save_steps={TRAINING_CONFIG["save_steps"]},
    fp16={TRAINING_CONFIG["fp16"]},
    optim="{TRAINING_CONFIG["optim"]}",
    lr_scheduler_type="{TRAINING_CONFIG["lr_scheduler_type"]}",
    max_grad_norm={TRAINING_CONFIG["max_grad_norm"]},
    max_steps={TRAINING_CONFIG["max_steps"]},
    group_by_length={TRAINING_CONFIG["group_by_length"]},
    report_to="{TRAINING_CONFIG["report_to"]}"
)

# Format dataset
def formatting_func(examples):
    return [f"### Question: {{ex['instruction']}}\\n\\n### Answer: {{ex['output']}}" for ex in examples]

# Trainer
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    args=training_args,
    formatting_func=formatting_func,
    max_seq_length=512
)

# Train
print("Starting fine-tuning...")
trainer.train()

# Save
print("Saving model...")
trainer.save_model("{OUTPUT_PATH}")
tokenizer.save_pretrained("{OUTPUT_PATH}")

print("Fine-tuning complete!")
print(f"Model saved to: {OUTPUT_PATH}")
'''

    script_path = OUTPUT_PATH / "finetune.py"
    script_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"Training script created: {script_path}")
    return script_path

def create_modal_run_script():
    """Create Modal script to run fine-tuning"""
    script = f'''#!/usr/bin/env python3
"""
GenTech DeFi Model — Modal Runner
Runs fine-tuning on BlockRun Modal with GPU
"""

import modal

app = modal.App("gentech-defi-model")

# Container image
image = (
    modal.Image.debian_slim(python_version="3.10")
    .pip_install(
        "torch",
        "transformers",
        "peft",
        "trl",
        "datasets",
        "bitsandbytes",
        "accelerate"
    )
)

@app.function(
    image=image,
    gpu="A10G",  # Good balance of cost and performance
    timeout=3600  # 1 hour timeout
)
def finetune():
    import torch
    from datasets import load_dataset
    from transformers import (
        AutoModelForCausalLM,
        AutoTokenizer,
        BitsAndBytesConfig,
        TrainingArguments
    )
    from peft import (
        LoraConfig,
        get_peft_model,
        prepare_model_for_kbit_training
    )
    from trl import SFTTrainer
    
    print("Starting fine-tuning on Modal...")
    
    # Load dataset
    dataset = load_dataset("json", data_files="{TRAINING_DATA_PATH}", split="train")
    
    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        "{MODEL_NAME}",
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("{MODEL_NAME}", trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    # LoRA config
    lora_config = LoraConfig(
        r={QLORA_CONFIG["r"]},
        lora_alpha={QLORA_CONFIG["lora_alpha"]},
        lora_dropout={QLORA_CONFIG["lora_dropout"]},
        target_modules={QLORA_CONFIG["target_modules"]},
        bias="{QLORA_CONFIG["bias"]}",
        task_type="{QLORA_CONFIG["task_type"]}"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="{TRAINING_CONFIG["output_dir"]}",
        num_train_epochs={TRAINING_CONFIG["num_train_epochs"]},
        per_device_train_batch_size={TRAINING_CONFIG["per_device_train_batch_size"]},
        gradient_accumulation_steps={TRAINING_CONFIG["gradient_accumulation_steps"]},
        learning_rate={TRAINING_CONFIG["learning_rate"]},
        weight_decay={TRAINING_CONFIG["weight_decay"]},
        warmup_steps={TRAINING_CONFIG["warmup_steps"]},
        logging_steps={TRAINING_CONFIG["logging_steps"]},
        save_steps={TRAINING_CONFIG["save_steps"]},
        fp16={TRAINING_CONFIG["fp16"]},
        optim="{TRAINING_CONFIG["optim"]}",
        lr_scheduler_type="{TRAINING_CONFIG["lr_scheduler_type"]}",
        max_grad_norm={TRAINING_CONFIG["max_grad_norm"]},
        max_steps={TRAINING_CONFIG["max_steps"]},
        group_by_length={TRAINING_CONFIG["group_by_length"]},
        report_to="{TRAINING_CONFIG["report_to"]}"
    )
    
    # Format dataset
    def formatting_func(examples):
        return [f"### Question: {{ex['instruction']}}\\n\\n### Answer: {{ex['output']}}" for ex in examples]
    
    # Trainer
    trainer = SFTTrainer(
        model=model,
        train_dataset=dataset,
        args=training_args,
        formatting_func=formatting_func,
        max_seq_length=512
    )
    
    # Train
    print("Starting fine-tuning...")
    trainer.train()
    
    # Save
    print("Saving model...")
    trainer.save_model("{OUTPUT_PATH}")
    tokenizer.save_pretrained("{OUTPUT_PATH}")
    
    print("Fine-tuning complete!")
    print(f"Model saved to: {OUTPUT_PATH}")

if __name__ == "__main__":
    finetune()
'''

    script_path = OUTPUT_PATH / "run-modal.py"
    with open(script_path, 'w') as f:
        f.write(script)
    
    print(f"Modal runner created: {script_path}")
    return script_path

if __name__ == "__main__":
    print("Creating fine-tuning scripts...")
    create_training_script()
    create_modal_run_script()
    
    print("\nReady for Sunday!")
    print("\nTo run fine-tuning:")
    print("1. Fund BlockRun wallet if needed")
    print("2. Run: python3 run-modal.py")
    print("3. Wait ~1 hour for training to complete")
    print("4. Model will be saved to: {OUTPUT_PATH}")
