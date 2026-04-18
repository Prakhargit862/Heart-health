# 🫀 Heart Health Prediction System

## 📌 Overview

This project is an AI-powered web application that predicts the risk of heart disease based on patient health parameters. It combines machine learning, data analysis, and an interactive web interface to provide real-time risk assessment and insights.

The system allows users to input medical data and receive:

- Risk prediction (High / Low)  
- Probability score  
- Visual analytics dashboard  
- Health recommendations  

---

## 🚀 Features

### 🔍 1. Heart Disease Prediction
- Predicts cardiac risk using a trained machine learning model  
- Accepts 13 clinical input features (age, cholesterol, BP, etc.)  
- Provides probability-based output  

---

### 📊 2. Interactive Dashboard
- Visualizes trends in predictions over time  
- Displays:
  - Risk distribution  
  - Cholesterol vs Age  
  - Heart rate analysis  
- Built using Plotly for dynamic charts  

---

### 🧠 3. Machine Learning Model
- Trained classification model (Scikit-learn)  
- Handles:
  - Data preprocessing  
  - Feature-based prediction  
  - Probability estimation  

---

### 🌐 4. Web Application (Flask)
- Fully functional backend using Flask  
- Routes:
  - `/` → Input form  
  - `/predict` → Prediction logic  
  - `/dashboard` → Analytics view  
- Maintains prediction history in memory  

---

### 📷 5. Image-Based Input (Advanced Feature)
- Upload medical reports (simulated processing)  
- Extracts data and generates prediction  
- Demonstrates extensibility (OCR integration possible)  

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask  
- **Machine Learning:** Scikit-learn, NumPy, Pandas  
- **Visualization:** Plotly  
- **Frontend:** HTML, CSS, JavaScript  
- **Model Storage:** Joblib  

---


git clone https://github.com/your-username/heart-health-project.git
cd heart-health-project
pip install flask numpy pandas scikit-learn plotly joblib
python app.py
http://127.0.0.1:5000 

___

## 📊 Input Features

The model uses the following medical parameters:

- Age  
- Sex  
- Chest Pain Type  
- Resting Blood Pressure  
- Cholesterol  
- Fasting Blood Sugar  
- Rest ECG  
- Max Heart Rate  
- Exercise-Induced Angina  
- Oldpeak  
- Slope  
- Number of Vessels (ca)  
- Thalassemia  

---

## 📈 Sample Output

- **Prediction:** High Risk / Low Risk  
- **Probability Score:** e.g., 78%  
- **Visualization:** Gauge chart + trend graphs  
- **Recommendation:** Lifestyle or clinical advice  

---

## 💡 Key Highlights

- End-to-end ML pipeline (data → model → UI)  
- Real-world healthcare use case  
- Clean UI with interactive analytics  

### Combines:
- Data Science  
- Backend Development  
- Data Visualization  

---

## ⚠️ Disclaimer

This project is for educational purposes only and should not be used as a substitute for professional medical advice.
