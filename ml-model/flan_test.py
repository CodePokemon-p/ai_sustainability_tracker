from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load model
model_name = "google/flan-t5-small"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# Example eco-tracker input
input_text = """
The product has greenhouse gas emissions: 25 kgCO2,
water consumption: 150 liters,
energy consumption: 10 kWh,
pollutants emitted: 2 units,
waste generation: 3 kg.
Please classify the eco level (Low, Moderate, High) and give short suggestions.
"""

# Encode and generate
inputs = tokenizer(input_text, return_tensors="pt")
outputs = model.generate(**inputs, max_length=150)

# Decode and print
print("\nGenerated Response:\n")
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
