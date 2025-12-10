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
   <img width="780" height="415" alt="image" src="https://github.com/user-attachments/assets/e5cb35d8-8278-498e-ae79-75a8ade6ac18" />
      Figure 1: Fronted dashboard showing real-time optimization result.

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

## 📦 Additional Project Resources

Some project components (due to large size) are hosted externally.

You can download them here:  
🔗 **Google Drive Link:** [Click to access backend, model, and environment folders](https://drive.google.com/drive/folders/10suWg5OIHMBZnAicmI9WiYjzEHoeb1QX?usp=sharing+
+)

**Included in Drive:**
- `backend/` folder (Node + Flask backend)
- `flan-env/` (Python virtual environment)
- `ml-model/` (trained machine learning model files)
- `node_modules/` (local dependencies)

> These files are excluded from GitHub due to size limits.  
> Please extract them in the root project directory after download.

---

## ⚙️ Security+ Threshold

- JWT authentication, secure hosting, and model input validation  
- Ensures **10% tolerance** for prediction/utilization deviation  
- Enterprise-level **security, reproducibility, and data integrity**

---

## 🧠 Tech Stack

**Frontend:** React, Tailwind CSS, Framer Motion, AOS, React Router  
**Backend:** Node.js / Express, MongoDB, JWT Auth  
**AI / ML Microservices:** Python / Flask, Gemini-based RLCV Regression Model  
**File Management:** Git LFS for large files (.pkl, .csv, .zip, .dxf)

---

## 🚀 Quick Setup Steps

**1️⃣ Clone repository with Git LFS:**
```bash
git lfs install
git clone https://github.com/CodePokemon-p/ai_sustainability_tracker.git
cd ai_sustainability_tracker
2️⃣ Install Python dependencies:
pip install -r requirements.txt
3️⃣ Install Node.js dependencies:

# Frontend
cd frontend
npm install

# Backend
cd ../backend
npm install
🧩 Running the Project
Frontend


cd frontend
npm run dev
Backend (Node.js)


cd backend
node server.js
ML / Flask Services


cd ml-model

# Run Tracker or Pattern Optimizer
python app.py
python pattern_app.py

# Run Report Analyzer
python analyzer.py

# Run MessageAlert or EcoBot AI Chatbot
uvicorn eco_bot:app --reload --port 8000
🌱 Usage
Access the Tracker Dashboard via frontend

Upload CSV / PDF reports to analyze sustainability metrics

Use Pattern Layout Optimizer to generate efficient fabric layouts

Interact with EcoBot AI Chatbot for sustainability guidance

Managers can send alerts/messages visible to employees in the Alert Center

🤝 Contributing
Fork the repository and create a new branch for your feature

Track large files using Git LFS

Submit pull requests with clear descriptions of your changes

📜 License
This project is licensed under the MIT License

📝 Notes
Large files (.pkl, .csv, .zip, .dxf) are managed using Git LFS

For local development, always ensure:

git lfs install
git pull
Security+ Threshold ensures enterprise-grade protection and reproducibility
