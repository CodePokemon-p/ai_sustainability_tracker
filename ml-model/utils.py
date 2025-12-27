import re

def extract_metrics_from_text(text):
    metrics = {}

    co2_match = re.search(r'(CO2|carbon dioxide)[^\d]*(\d+\.?\d*)', text, re.IGNORECASE)
    water_match = re.search(r'(water)[^\d]*(\d+\.?\d*)', text, re.IGNORECASE)
    energy_match = re.search(r'(energy)[^\d]*(\d+\.?\d*)', text, re.IGNORECASE)
    waste_match = re.search(r'(waste)[^\d]*(\d+\.?\d*)', text, re.IGNORECASE)

    if co2_match: metrics['CO₂ Emissions (tons)'] = float(co2_match.group(2))
    if water_match: metrics['Water Consumption (liters)'] = float(water_match.group(2))
    if energy_match: metrics['Energy Use (kWh)'] = float(energy_match.group(2))
    if waste_match: metrics['Waste Generation (kg)'] = float(waste_match.group(2))

    return metrics or {'message': 'No sustainability metrics detected'}
