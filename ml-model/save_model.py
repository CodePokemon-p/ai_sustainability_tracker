from transformers import AutoModelForSeq2SeqLM

# Load the fine-tuned model checkpoint
model = AutoModelForSeq2SeqLM.from_pretrained("./flan_t5_finetuned")

# Save properly to a new folder (avoid Windows locking issue)
model.save_pretrained("./flan_t5_model", safe_serialization=False)

print("✅ Model saved successfully to ./flan_t5_model/")
