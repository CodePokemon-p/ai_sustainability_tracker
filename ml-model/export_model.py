from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

# 1) Your final checkpoint with trained weights
CKPT = "./flan_t5_finetuned/checkpoint-5217"

# 2) Get tokenizer from the base model (checkpoints usually don't have tokenizer files)
BASE_TOK = "google/flan-t5-small"

# 3) Output directory for a clean, ready-to-serve model
OUT = "./flan_t5_model"

print("🔄 Loading model weights from", CKPT)
model = AutoModelForSeq2SeqLM.from_pretrained(CKPT)

print("🔄 Loading tokenizer from base model:", BASE_TOK)
# use_fast=True avoids the slow SentencePiece dependency path
tokenizer = AutoTokenizer.from_pretrained(BASE_TOK, use_fast=True)

print("💾 Saving clean model folder to", OUT)
# write a standard pytorch_model.bin (not just safetensors)
model.save_pretrained(OUT, safe_serialization=False)
tokenizer.save_pretrained(OUT)

print("✅ Export complete. Use folder:", OUT)
