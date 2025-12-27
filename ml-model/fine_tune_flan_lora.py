# fine_tune_flan_lora.py
"""
Fine-tune google/flan-t5-small with LoRA (PEFT).
- Uses bitsandbytes 8-bit quantization when CUDA is available.
- Falls back to non-quantized CPU mode when no GPU is present.
- Expects a CSV file named `synthetic_flan_dataset.csv` with columns:
    input_text,output_text
"""

import os
import math
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
    DataCollatorForSeq2Seq,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training

# -------------------------
# Config - edit if needed
# -------------------------
CSV_FILE = "synthetic_flan_dataset.csv"   # must exist in working dir
MODEL_NAME = "google/flan-t5-small"
OUTPUT_DIR = "./flan_lora_results"
NUM_EPOCHS = 3

# -------------------------
# Environment checks
# -------------------------
use_cuda = torch.cuda.is_available()
print(f"CUDA available: {use_cuda}")

# If using CPU only, reduce batch size to avoid OOM
if use_cuda:
    per_device_batch = 4
else:
    per_device_batch = 1

# -------------------------
# Load dataset
# -------------------------
if not os.path.exists(CSV_FILE):
    raise FileNotFoundError(f"Required CSV not found: {CSV_FILE}\nCreate a file with columns: input_text,output_text")

print("Loading dataset...")
dataset = load_dataset("csv", data_files={"train": CSV_FILE})

# -------------------------
# Tokenizer + Model load
# -------------------------
print("Loading tokenizer and model...")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)

if use_cuda:
    # Configure bitsandbytes quantization
    bnb_config = BitsAndBytesConfig(
        load_in_8bit=True,
        llm_int8_threshold=6.0,
        llm_int8_has_fp16_weight=False
    )
    model = AutoModelForSeq2SeqLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=False
    )
    # Prepare model for k-bit training (PEFT helper)
    model = prepare_model_for_kbit_training(model)
else:
    # CPU fallback (no quantization)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME, device_map={"": "cpu"})
    # do NOT call prepare_model_for_kbit_training when no quantization

# -------------------------
# Configure LoRA (PEFT)
# -------------------------
print("Applying LoRA configuration...")
lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q", "v"],  # common T5 attention modules
    lora_dropout=0.05,
    bias="none",
    task_type="SEQ_2_SEQ_LM"
)
model = get_peft_model(model, lora_config)

# -------------------------
# Preprocessing / Tokenization
# -------------------------
max_input_length = 128
max_target_length = 256

def preprocess_function(examples):
    inputs = examples["input_text"]
    targets = examples["output_text"]
    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True, padding="max_length")
    with tokenizer.as_target_tokenizer():
        labels = tokenizer(targets, max_length=max_target_length, truncation=True, padding="max_length")
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

print("Tokenizing dataset (this may take a bit)...")
tokenized = dataset["train"].map(preprocess_function, batched=True, remove_columns=dataset["train"].column_names)

# -------------------------
# Data collator & Trainer
# -------------------------
data_collator = DataCollatorForSeq2Seq(tokenizer, model=model)

# pick training args appropriate for GPU/CPU
training_args = TrainingArguments(
    output_dir=OUTPUT_DIR,
    per_device_train_batch_size=per_device_batch,
    gradient_accumulation_steps=math.ceil(8 / max(1, per_device_batch)),  # keep effective batch ~8
    num_train_epochs=NUM_EPOCHS,
    learning_rate=2e-4,
    fp16=True if use_cuda else False,
    logging_steps=50,
    save_steps=200,
    save_total_limit=2,
    remove_unused_columns=False,
    push_to_hub=False,
    report_to="none"
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=data_collator
)

# -------------------------
# Train
# -------------------------
print("Starting training...")
trainer.train()

# -------------------------
# Save
# -------------------------
print("Saving LoRA-tuned model and tokenizer...")
model.save_pretrained(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print("✅ Fine-tuning finished. Saved to:", OUTPUT_DIR)
