import pandas as pd
import random

def create_dynamic_synthetic_data(num_samples=2000):
    data = []
    
    eco_levels = ["low", "moderate", "high"]
    modes = ["professional", "friendly"]
    product_types = ["Cotton", "Polyester", "Nylon", "Linen", "Silk", "Wool", "Denim", "Viscose", "Recycled_Poly", "Organic_Cotton"]
    
    # Environmental metrics ranges
    metric_ranges = {
        "low": {"ghg": (150, 300), "water": (200, 500), "energy": (100, 250), "waste": (80, 200), "pollutants": (100, 300)},
        "moderate": {"ghg": (80, 150), "water": (100, 200), "energy": (60, 100), "waste": (40, 80), "pollutants": (50, 100)},
        "high": {"ghg": (20, 80), "water": (50, 100), "energy": (30, 60), "waste": (10, 40), "pollutants": (10, 50)}
    }
    
    for i in range(num_samples):
        eco_level = random.choice(eco_levels)
        mode = random.choice(modes)
        product_type = random.choice(product_types)
        
        # Generate realistic metrics based on eco level
        metrics = metric_ranges[eco_level]
        ghg = random.randint(*metrics["ghg"])
        water = random.randint(*metrics["water"])
        energy = random.randint(*metrics["energy"])
        waste = random.randint(*metrics["waste"])
        pollutants = random.randint(*metrics["pollutants"])
        
        # Create PROMPT (input) - Include metrics for context!
        prompt = f"Eco Level: {eco_level} | Mode: {mode} | Product: {product_type} | Metrics: GHG={ghg}, Water={water}, Energy={energy}, Waste={waste}, Pollutants={pollutants}"
        
        # Create DIVERSE RESPONSES (output)
        if eco_level == "high":
            responses = [
                f"Reason: Exceptional environmental performance with carbon emissions of only {ghg} units, far below industry average. {product_type} production shows excellent resource management with water consumption at {water} units. Suggestion: Consider achieving carbon-negative status and implementing biodiversity enhancement programs. Prediction: Leadership in sustainability will drive market differentiation and premium pricing opportunities.",
                f"Reason: Outstanding eco-efficiency with energy consumption at {energy} MWh and waste generation limited to {waste} tons, setting new industry benchmarks for {product_type} manufacturing. Suggestion: Explore circular economy certification and green bond financing for expansion. Prediction: Sustainable competitive advantage will attract ESG investors and conscious consumers.",
                f"Reason: World-class environmental stewardship with pollutant emissions of merely {pollutants} kg, demonstrating superior operational controls in {product_type} production. Suggestion: Develop sustainability training programs for industry peers and pursue UN SDG alignment. Prediction: Position as environmental leader will open new market opportunities and partnerships."
            ]
        elif eco_level == "moderate":
            responses = [
                f"Reason: Satisfactory environmental performance with {ghg} tons CO2 emissions and {water} m³ water usage meeting basic compliance standards for {product_type}. Suggestion: Implement smart monitoring systems to reduce energy consumption from current {energy} MWh by 20-30%. Prediction: Targeted improvements could achieve high eco-rating within 9-12 months.",
                f"Reason: Transitional sustainability phase with waste generation at {waste} tons and pollutants at {pollutants} kg indicating need for optimization in {product_type} production. Suggestion: Adopt lean manufacturing and water recycling to improve efficiency. Prediction: Gradual enhancement expected with consistent implementation of best practices.",
                f"Reason: Balanced environmental impact with current metrics showing potential for significant improvement in {product_type} manufacturing. Energy usage at {energy} MWH and water at {water} m³ suggest efficiency opportunities. Suggestion: Conduct energy audit and implement ISO 50001 standards. Prediction: 25-40% improvement achievable with systematic approach."
            ]
        else:  # low
            responses = [
                f"Reason: Critical environmental challenges with {ghg} tons CO2 emissions exceeding sustainable limits by 60% for {product_type} production. Water consumption of {water} m³ requires immediate reduction strategies. Suggestion: Emergency implementation of carbon capture technology and water recycling systems. Prediction: Without urgent action, regulatory interventions and reputational damage imminent.",
                f"Reason: Severe environmental impact with energy consumption at {energy} MWh and waste generation of {waste} tons indicating systemic inefficiencies in {product_type} manufacturing. Pollutant levels at {pollutants} kg require immediate remediation. Suggestion: Complete operational overhaul with focus on renewable transition. Prediction: Transformational change needed to avoid financial penalties.",
                f"Reason: Unsustainable practices across all metrics with greenhouse gases at {ghg} tons, water usage at {water} m³, and pollutants at {pollutants} kg exceeding all benchmarks for {product_type}. Suggestion: Implement emergency sustainability task force and rapid technology adoption. Prediction: Existential business risk without immediate comprehensive action."
            ]
        
        # Add tone variations
        if mode == "friendly":
            responses = [r.replace("Reason:", "Hey there! 🌍 Here's why:").replace("Suggestion:", "How about we try:").replace("Prediction:", "Looking ahead:") for r in responses]
            responses = [r + " You've got this! 💚" for r in responses]
        
        response = random.choice(responses)
        data.append({"prompt": prompt, "response": response})
        
        # Show progress
        if (i + 1) % 500 == 0:
            print(f"✅ Generated {i + 1} samples...")
    
    return pd.DataFrame(data)

# Generate data
print("🚀 Creating dynamic training data...")
df = create_dynamic_synthetic_data(2500)
df.to_csv("dynamic_training_data.csv", index=False)
print("✅ Created 2500 diverse training samples!")
print("📊 Sample preview:")
print(df.head(3))