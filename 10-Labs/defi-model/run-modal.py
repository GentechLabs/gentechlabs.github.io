#!/usr/bin/env python3
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
    dataset = load_dataset("json", data_files="/root/vaults/gentech/02-Labs/defi-model/final-training-20260618.jsonl", split="train")
    
    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )
    
    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained("deepseek-ai/DeepSeek-R1-Distill-Qwen-32B", trust_remote_code=True)
    tokenizer.pad_token = tokenizer.eos_token
    
    # Prepare model for training
    model = prepare_model_for_kbit_training(model)
    
    # LoRA config
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        bias="none",
        task_type="CAUSAL_LM"
    )
    
    # Apply LoRA
    model = get_peft_model(model, lora_config)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="/root/vaults/gentech/02-Labs/defi-model/model",
        num_train_epochs=3,
        per_device_train_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_steps=100,
        logging_steps=10,
        save_steps=100,
        fp16=True,
        optim="paged_adamw_32bit",
        lr_scheduler_type="cosine",
        max_grad_norm=0.3,
        max_steps=-1,
        group_by_length=True,
        report_to="none"
    )
    
    # Format dataset
    def formatting_func(examples):
        return [f"### Question: {ex['instruction']}\n\n### Answer: {ex['output']}" for ex in examples]
    
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
    trainer.save_model("/root/vaults/gentech/02-Labs/defi-model/model")
    tokenizer.save_pretrained("/root/vaults/gentech/02-Labs/defi-model/model")
    
    print("Fine-tuning complete!")
    print("Model saved to: /root/vaults/gentech/02-Labs/defi-model/model")

if __name__ == "__main__":
    finetune()
