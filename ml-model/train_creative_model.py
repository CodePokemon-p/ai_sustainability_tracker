from transformers import (
    AutoTokenizer, AutoModelForSeq2SeqLM, 
    Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
)
from peft import LoraConfig, get_peft_model, TaskType
import pandas as pd
from datasets import Dataset
import torch

# Load model
model_name = "google/flan-t5-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Load dynamic data
df = pd.read_csv("dynamic_training_data.csv")
dataset = Dataset.from_pandas(df)

# Tokenization
def preprocess_function(examples):
    inputs = [p for p in examples["prompt"]]
    targets = [r for r in examples["response"]]
    
    model_inputs = tokenizer(inputs, max_length=256, truncation=True, padding="max_length")
    labels = tokenizer(targets, max_length=256, truncation=True, padding="max_length")
    
    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

tokenized_dataset = dataset.map(preprocess_function, batched=True)

# LoRA Config for creativity
lora_config = LoraConfig(
    task_type=TaskType.SEQ_2_SEQ_LM,
    r=16,  # Higher rank for more creativity
    lora_alpha=32,
    lora_dropout=0.1,
    target_modules=["q", "v", "k", "o"]  # More modules for better learning
)

model = get_peft_model(model, lora_config)

# Training arguments for creativity
training_args = Seq2SeqTrainingArguments(
    output_dir="./creative-flan-model",
    learning_rate=2e-4,  # Slightly higher for creativity
    per_device_train_batch_size=4,
    num_train_epochs=7,  # More epochs for better learning
    logging_steps=50,
    save_steps=500,
    predict_with_generate=True,
    fp16=True,
    warmup_steps=100,
    weight_decay=0.01,
    save_total_limit=2,
)

trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
    data_collator=DataCollatorForSeq2Seq(tokenizer, model=model),
)

print("🚀 Training creative Flan model...")
trainer.train()
trainer.save_model()
tokenizer.save_pretrained("./creative-flan-model")
print("✅ Creative model trained and saved!")