from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# ----------------------------
# FastAPI app
# ----------------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Request body
# ----------------------------
class Message(BaseModel):
    text: str

# ----------------------------
# Load BERT model & tokenizer
# ----------------------------
MODEL_NAME = "bert-base-multilingual-uncased"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModel.from_pretrained(MODEL_NAME)
model.eval()

# ----------------------------
# Predefined questions & responses
# ----------------------------
PREDEFINED_QUESTIONS = [
    "How to reduce CO2 emissions?",
    "How to reduce carbon footprint?",
    "Ways to reduce carbon?",
    "How to save water in production?",
    "How to reduce water consumption?",
    "How to reduce waste?",
    "How to recycle waste?",
    "کاربن کے اخراج کو کم کرنے کے لیے اقدامات",
    "پانی کے استعمال کو کم کرنے کے لیے اقدامات",
    "فضلہ کم کرنے کے لیے اقدامات"
]

PREDEFINED_RESPONSES = [
    "🌿 EcoBot: Try reducing CO₂ emissions by using energy-efficient machines or renewable energy sources.",
    "🌿 EcoBot: Try reducing CO₂ emissions by using energy-efficient machines or renewable energy sources.",
    "🌿 EcoBot: Reduce carbon footprint by optimizing energy, reducing travel, and using sustainable resources.",
    "💧 EcoBot: Reduce water usage by recycling water and using low-flow systems.",
    "💧 EcoBot: Reduce water usage by recycling water and using low-flow systems.",
    "♻️ EcoBot: Implement waste segregation and recycling to minimize waste.",
    "♻️ EcoBot: Implement waste segregation and recycling to minimize waste.",
    "🌿 EcoBot: Try reducing CO₂ emissions by using energy-efficient machines or renewable energy sources.",
    "💧 EcoBot: Reduce water usage by recycling water and using low-flow systems.",
    "♻️ EcoBot: Implement waste segregation and recycling to minimize waste."
]

# ----------------------------
# Precompute embeddings
# ----------------------------
predefined_embeddings = []
with torch.no_grad():
    for q in PREDEFINED_QUESTIONS:
        inputs = tokenizer(q, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        emb = outputs.last_hidden_state[:, 0, :]
        emb = F.normalize(emb, p=2, dim=1)
        predefined_embeddings.append(emb)

# ----------------------------
# Generate response
# ----------------------------
def generate_response(text: str):
    text_clean = text.strip()
    
    # Quick greeting handling
    greetings = ["hi", "hello", "hey", "bruh", "yo"]
    if any(g.lower() in text_clean.lower() for g in greetings):
        return "🌿 EcoBot: Hello! Ask me anything about sustainability and eco-friendly practices."
    
    # Compute embedding
    with torch.no_grad():
        inputs = tokenizer(text_clean, return_tensors="pt", truncation=True, padding=True)
        outputs = model(**inputs)
        query_emb = outputs.last_hidden_state[:, 0, :]
        query_emb = F.normalize(query_emb, p=2, dim=1)
    
    # Cosine similarity
    sims = [F.cosine_similarity(query_emb, emb, dim=1).item() for emb in predefined_embeddings]
    max_sim = max(sims)
    max_idx = sims.index(max_sim)
    
    # Flexible threshold
    if max_sim >= 0.72:  # slightly lower threshold for recall
        return PREDEFINED_RESPONSES[max_idx]
    
    # Keyword fallback
    low_text = text_clean.lower()
    if any(k in low_text for k in ["carbon", "co2", "greenhouse", "emission"]):
        return "🌿 EcoBot: Reduce carbon footprint by using renewable energy, energy-efficient processes, and minimizing travel."
    elif any(k in low_text for k in ["water", "pani", "consumption"]):
        return "💧 EcoBot: Conserve water by recycling and using low-flow systems."
    elif any(k in low_text for k in ["waste", "recycle", "فضلہ"]):
        return "♻️ EcoBot: Implement proper waste segregation and recycling to minimize environmental impact."
    
    return "🤖 EcoBot: I'm still learning! Can you rephrase your sustainability question?"

# ----------------------------
# API route
# ----------------------------
@app.post("/api/chat")
async def chat(message: Message):
    reply = generate_response(message.text)
    return {"reply": reply}

# ----------------------------
# Run server
# ----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("eco_bot:app", host="127.0.0.1", port=8000, reload=True)
