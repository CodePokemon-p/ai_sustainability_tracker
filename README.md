# AI Sustainability Tracker

**Project:** AI Sustainability Tracker for Textile Factories & Eco-Brands  
**Author:** Saba Saleem  
**Repo:** (https://github.com/CodePokemon-p/ai_sustainability_tracker)

---

## Project Overview

The **AI Sustainability Tracker** is a comprehensive tool designed for textile factories and eco-conscious brands to **track, analyze, and optimize environmental impact**. The platform monitors key sustainability metrics such as CO₂ emissions, water consumption, energy usage, waste generation, and pollutants.

It also integrates **AI-driven analytics**, predictive alerts, and interactive tools for improved decision-making and sustainable production practices.

---

## Key Features

### Tracker Tool
- Track CO₂ emissions, water consumption, energy consumption, waste, and pollutants.
- Provides **professional analysis** with primary driver, risk, and actionable recommendations.
- Supports multiple product types: Recycled Poly, Organic Cotton, Synthetic Blend, Microfiber.
- Multi-line, concise dashboard analytics.
- Run via  (python app.py)

### AI Pattern Layout Optimizer
- Uses a **Genetic Algorithm (GA)** and **Computer Vision (CV)** to optimize fabric layouts.
- Maximizes utilization (80–90%) and reduces fabric waste.
- Generates **DXF files** for production.
-  Run via (python pattern_app.py)

### Report Analyzer
- Upload CSV or PDF reports to analyze environmental metrics.
- Generates automated analytics with clear sustainability insights.
- Run via `Python analyzer.py`.

### MessageAlert
- Allows managers to send messages/alerts to employees or brand members.
- Messages appear in the **Alert Center** for real-time communication.
- Run via `Python app.py` in the respective Flask folder.

### EcoBoot AI Chatbot
- Interactive AI chatbot for discussing sustainability practices.
- Provides guidance and answers questions related to environmental impact.
- Run backend with: uvicorn eco_bot:app --reload --port 8000

```bash
uvicorn eco_bot:app --reload --port 8000
Security+ Threshold
JWT authentication, secure hosting, and model input validation.

Ensures 10% tolerance for prediction/utilization deviation.

Enterprise-level security and reproducibility built-in.

Tech Stack
Frontend: React, Tailwind CSS, Framer Motion, AOS, React Router

Backend: Node.js / Express, MongoDB, JWT Auth

AI / ML Microservices: Python / Flask, Gemini-based RLCV Regression Model

File Management: Git LFS for large files (.pkl, .csv, .zip, .dxf)

Installation & Setup
Clone repository with Git LFS:

git lfs install
git clone https://github.com/CodePokemon-p/ai_sustainability_tracker.git
cd ai_sustainability_tracker
Install Python dependencies:


pip install -r requirements.txt
Install Node.js dependencies:


# Frontend
cd frontend
npm install

# Backend
cd ../backend
npm install
Running the Project
Frontend

cd frontend
npm run dev
Backend (Node.js)

cd backend
node node-server.js
ML/Flask Services
All Flask-related tools are in the ml-model folder:


cd ml-model

# Run Tracker/Pattern Optimizer
python app.py
python pattern_app.py

# Run Report Analyzer
python analyzer.py

# Run MessageAlert
python app.py
EcoBoot AI Chatbot
# uvicorn eco_bot:app --reload --port 8000
Usage
Access the tracker dashboard via frontend.

Upload CSV/PDF reports to analyze sustainability metrics.

Use the Pattern Layout Optimizer to generate fabric layouts.

Interact with EcoBoot AI Chatbot for sustainability guidance.

Managers can send alerts/messages using MessageAlert, visible to employees in the Alert Center.

Contributing
Fork the repository and create a new branch for your feature.

Track large files using Git LFS.

Submit pull requests with detailed descriptions of changes.

License
This project is licensed under the MIT License.

Notes
Large files (.pkl, .csv, .zip, .dxf) are managed using Git LFS.

For local development, always ensure:


git lfs install
git pull
Security+ Threshold ensures enterprise-level security, reproducibility, and data integrity.
