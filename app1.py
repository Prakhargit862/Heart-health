from flask import Flask, request, jsonify
import base64
import json
import os

app = Flask(__name__)

# HTML template embedded in Python
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Predicting Heart Health</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0f172a 100%);
            color: white;
            min-height: 100vh;
            padding: 2rem;
            position: relative;
            overflow-x: hidden;
        }

        .bg-animation {
            position: fixed;
            inset: 0;
            overflow: hidden;
            pointer-events: none;
            z-index: 0;
        }

        .bg-blob {
            position: absolute;
            border-radius: 50%;
            filter: blur(100px);
            opacity: 0.2;
            animation: float 20s infinite ease-in-out;
        }

        .bg-blob-1 {
            width: 400px;
            height: 400px;
            background: #3b82f6;
            top: -100px;
            left: -100px;
        }

        .bg-blob-2 {
            width: 400px;
            height: 400px;
            background: #8b5cf6;
            bottom: -100px;
            right: -100px;
            animation-delay: 5s;
        }

        @keyframes float {
            0%, 100% { transform: translate(0, 0) scale(1); }
            33% { transform: translate(50px, -50px) scale(1.1); }
            66% { transform: translate(-50px, 50px) scale(0.9); }
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.8; }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
            animation: fadeIn 0.6s ease-out;
        }

        .header {
            text-align: center;
            margin-bottom: 3rem;
        }

        .heart-icon {
            font-size: 4rem;
            color: #ef4444;
            animation: pulse 2s infinite;
            display: inline-block;
            margin-bottom: 1rem;
        }

        h1 {
            font-size: 3rem;
            background: linear-gradient(to right, #60a5fa, #a78bfa);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 1rem;
        }

        .subtitle {
            color: #9ca3af;
            font-size: 1.2rem;
        }

        .main-card {
            background: rgba(15, 23, 42, 0.5);
            backdrop-filter: blur(20px);
            border-radius: 2rem;
            padding: 2rem;
            box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(148, 163, 184, 0.1);
            transition: all 0.3s ease;
        }

        .main-card:hover {
            box-shadow: 0 25px 50px -12px rgba(59, 130, 246, 0.3);
        }

        .mode-selector {
            display: flex;
            gap: 1rem;
            margin-bottom: 2rem;
        }

        .mode-btn {
            flex: 1;
            padding: 1rem;
            border: none;
            border-radius: 1rem;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
            background: #1e293b;
            color: white;
        }

        .mode-btn.active {
            background: linear-gradient(to right, #2563eb, #7c3aed);
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
        }

        .mode-btn:hover:not(.active) {
            background: #334155;
        }

        .form-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .form-group {
            display: flex;
            flex-direction: column;
            gap: 0.5rem;
        }

        label {
            font-size: 0.875rem;
            font-weight: 600;
            color: #d1d5db;
        }

        input, select {
            padding: 0.75rem;
            background: #1e293b;
            border: 1px solid #334155;
            border-radius: 0.75rem;
            color: white;
            font-size: 1rem;
            transition: all 0.3s ease;
        }

        input:focus, select:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }

        input::placeholder {
            color: #6b7280;
        }

        .image-upload-area {
            border: 2px dashed #334155;
            border-radius: 1.5rem;
            padding: 3rem;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            margin-bottom: 2rem;
        }

        .image-upload-area:hover {
            border-color: #3b82f6;
            background: rgba(59, 130, 246, 0.05);
        }

        .upload-icon {
            font-size: 4rem;
            color: #6b7280;
            margin-bottom: 1rem;
        }

        #imagePreview {
            max-width: 500px;
            margin: 1rem auto;
            border-radius: 1rem;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
            display: block;
        }

        .submit-btn {
            width: 100%;
            padding: 1rem;
            border: none;
            border-radius: 1rem;
            font-size: 1.125rem;
            font-weight: 700;
            cursor: pointer;
            background: linear-gradient(to right, #2563eb, #7c3aed);
            color: white;
            box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.5);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        .submit-btn:hover:not(:disabled) {
            box-shadow: 0 15px 30px -5px rgba(59, 130, 246, 0.7);
            transform: translateY(-2px);
        }

        .submit-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .spinner {
            width: 24px;
            height: 24px;
            border: 3px solid rgba(255, 255, 255, 0.3);
            border-top-color: white;
            border-radius: 50%;
            animation: spin 0.8s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .report-container {
            display: none;
            animation: fadeIn 0.6s ease-out;
        }

        .report-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2rem;
        }

        .report-header h2 {
            font-size: 2rem;
        }

        .new-analysis-btn {
            padding: 0.5rem 1.5rem;
            background: #1e293b;
            border: none;
            border-radius: 0.5rem;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .new-analysis-btn:hover {
            background: #334155;
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .stat-card {
            padding: 1.5rem;
            border-radius: 1.5rem;
            border: 1px solid;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
        }

        .stat-card.low {
            background: rgba(16, 185, 129, 0.1);
            border-color: rgba(16, 185, 129, 0.3);
        }

        .stat-card.moderate {
            background: rgba(251, 191, 36, 0.1);
            border-color: rgba(251, 191, 36, 0.3);
        }

        .stat-card.high {
            background: rgba(239, 68, 68, 0.1);
            border-color: rgba(239, 68, 68, 0.3);
        }

        .stat-card.info {
            background: rgba(59, 130, 246, 0.1);
            border-color: rgba(59, 130, 246, 0.3);
        }

        .stat-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
        }

        .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            margin-top: 0.5rem;
        }

        .parameters-card, .recommendations-card {
            background: rgba(30, 41, 59, 0.5);
            padding: 1.5rem;
            border-radius: 1.5rem;
            margin-bottom: 1.5rem;
        }

        .parameters-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .param-item {
            background: rgba(51, 65, 85, 0.5);
            padding: 1rem;
            border-radius: 0.75rem;
        }

        .param-label {
            font-size: 0.75rem;
            color: #9ca3af;
            margin-bottom: 0.25rem;
        }

        .param-value {
            font-size: 1.125rem;
            font-weight: 600;
        }

        .recommendations-list {
            list-style: none;
            margin-top: 1rem;
        }

        .recommendations-list li {
            padding: 0.75rem;
            margin-bottom: 0.75rem;
            background: rgba(51, 65, 85, 0.5);
            border-radius: 0.75rem;
            display: flex;
            gap: 0.75rem;
            align-items: flex-start;
        }

        .check-icon {
            color: #10b981;
            flex-shrink: 0;
            margin-top: 0.25rem;
        }

        .hidden {
            display: none;
        }

        .timestamp {
            text-align: center;
            color: #6b7280;
            margin-top: 2rem;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="bg-animation">
        <div class="bg-blob bg-blob-1"></div>
        <div class="bg-blob bg-blob-2"></div>
    </div>

    <div class="container">
        <div class="header">
            <div class="heart-icon">❤️</div>
            <h1>Predicting Heart Health</h1>
            <p class="subtitle">Advanced AI-Powered Cardiac Risk Assessment</p>
        </div>

        <div id="inputSection" class="main-card">
            <div class="mode-selector">
                <button class="mode-btn active" onclick="switchMode('form')">
                    <span>📝</span> Manual Input
                </button>
                <button class="mode-btn" onclick="switchMode('image')">
                    <span>📷</span> Upload Image
                </button>
            </div>

            <div id="formMode">
                <div class="form-grid">
                    <div class="form-group">
                        <label for="age">Age (years)</label>
                        <input type="number" id="age" placeholder="e.g., 45" required>
                    </div>

                    <div class="form-group">
                        <label for="sex">Sex</label>
                        <select id="sex" required>
                            <option value="">Select</option>
                            <option value="1">Male</option>
                            <option value="0">Female</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="cp">Chest Pain Type</label>
                        <select id="cp" required>
                            <option value="">Select</option>
                            <option value="0">Typical Angina</option>
                            <option value="1">Atypical Angina</option>
                            <option value="2">Non-anginal Pain</option>
                            <option value="3">Asymptomatic</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="trestbps">Resting BP (mm Hg)</label>
                        <input type="number" id="trestbps" placeholder="e.g., 120" required>
                    </div>

                    <div class="form-group">
                        <label for="chol">Cholesterol (mg/dl)</label>
                        <input type="number" id="chol" placeholder="e.g., 200" required>
                    </div>

                    <div class="form-group">
                        <label for="fbs">Fasting Blood Sugar > 120</label>
                        <select id="fbs" required>
                            <option value="">Select</option>
                            <option value="1">Yes</option>
                            <option value="0">No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="restecg">Resting ECG</label>
                        <select id="restecg" required>
                            <option value="">Select</option>
                            <option value="0">Normal</option>
                            <option value="1">ST-T Wave Abnormality</option>
                            <option value="2">Left Ventricular Hypertrophy</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="thalach">Max Heart Rate</label>
                        <input type="number" id="thalach" placeholder="e.g., 150" required>
                    </div>

                    <div class="form-group">
                        <label for="exang">Exercise Induced Angina</label>
                        <select id="exang" required>
                            <option value="">Select</option>
                            <option value="1">Yes</option>
                            <option value="0">No</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="oldpeak">Oldpeak (ST Depression)</label>
                        <input type="number" id="oldpeak" step="0.1" placeholder="e.g., 1.5" required>
                    </div>

                    <div class="form-group">
                        <label for="slope">Slope</label>
                        <select id="slope" required>
                            <option value="">Select</option>
                            <option value="0">Upsloping</option>
                            <option value="1">Flat</option>
                            <option value="2">Downsloping</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="ca">Major Vessels (0-3)</label>
                        <select id="ca" required>
                            <option value="">Select</option>
                            <option value="0">0</option>
                            <option value="1">1</option>
                            <option value="2">2</option>
                            <option value="3">3</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label for="thal">Thalassemia</label>
                        <select id="thal" required>
                            <option value="">Select</option>
                            <option value="0">Normal</option>
                            <option value="1">Fixed Defect</option>
                            <option value="2">Reversible Defect</option>
                        </select>
                    </div>
                </div>

                <button class="submit-btn" onclick="submitForm()">
                    <span>⚡</span> Generate Health Report
                </button>
            </div>

            <div id="imageMode" class="hidden">
                <div class="image-upload-area" onclick="document.getElementById('imageInput').click()">
                    <div class="upload-icon">📤</div>
                    <h3>Upload Medical Report</h3>
                    <p style="color: #9ca3af; margin-top: 0.5rem;">Click to select an image with patient data</p>
                </div>
                <input type="file" id="imageInput" accept="image/*" style="display: none;" onchange="handleImageSelect(event)">
                <img id="imagePreview" class="hidden">

                <button class="submit-btn" id="imageSubmitBtn" onclick="submitImage()" disabled>
                    <span>⚡</span> Analyze Image & Generate Report
                </button>
            </div>
        </div>

        <div id="reportSection" class="report-container">
            <div class="main-card">
                <div class="report-header">
                    <h2>Health Assessment Report</h2>
                    <button class="new-analysis-btn" onclick="resetForm()">New Analysis</button>
                </div>

                <div class="stats-grid">
                    <div class="stat-card" id="riskCard">
                        <div class="stat-icon">⚠️</div>
                        <h3>Risk Level</h3>
                        <div class="stat-value" id="riskLevel">-</div>
                    </div>

                    <div class="stat-card info">
                        <div class="stat-icon">📊</div>
                        <h3>Risk Score</h3>
                        <div class="stat-value" id="riskScore">-</div>
                    </div>

                    <div class="stat-card info">
                        <div class="stat-icon">✅</div>
                        <h3>Status</h3>
                        <div class="stat-value" style="font-size: 1.5rem;">Complete</div>
                    </div>
                </div>

                <div class="parameters-card">
                    <h3>Patient Parameters</h3>
                    <div class="parameters-grid" id="parametersGrid"></div>
                </div>

                <div class="recommendations-card">
                    <h3>Recommendations</h3>
                    <ul class="recommendations-list" id="recommendationsList"></ul>
                </div>

                <div class="timestamp" id="timestamp"></div>
            </div>
        </div>
    </div>

    <script>
        let currentMode = 'form';
        let uploadedImageData = null;

        function switchMode(mode) {
            currentMode = mode;
            const formMode = document.getElementById('formMode');
            const imageMode = document.getElementById('imageMode');
            const buttons = document.querySelectorAll('.mode-btn');

            buttons.forEach(btn => btn.classList.remove('active'));

            if (mode === 'form') {
                formMode.classList.remove('hidden');
                imageMode.classList.add('hidden');
                buttons[0].classList.add('active');
            } else {
                formMode.classList.add('hidden');
                imageMode.classList.remove('hidden');
                buttons[1].classList.add('active');
            }
        }

        function handleImageSelect(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    uploadedImageData = e.target.result;
                    const preview = document.getElementById('imagePreview');
                    preview.src = e.target.result;
                    preview.classList.remove('hidden');
                    document.getElementById('imageSubmitBtn').disabled = false;
                };
                reader.readAsDataURL(file);
            }
        }

        function getFormData() {
            return {
                age: document.getElementById('age').value,
                sex: document.getElementById('sex').value,
                cp: document.getElementById('cp').value,
                trestbps: document.getElementById('trestbps').value,
                chol: document.getElementById('chol').value,
                fbs: document.getElementById('fbs').value,
                restecg: document.getElementById('restecg').value,
                thalach: document.getElementById('thalach').value,
                exang: document.getElementById('exang').value,
                oldpeak: document.getElementById('oldpeak').value,
                slope: document.getElementById('slope').value,
                ca: document.getElementById('ca').value,
                thal: document.getElementById('thal').value
            };
        }

        function validateFormData(data) {
            for (let key in data) {
                if (!data[key]) {
                    alert('Please fill all fields');
                    return false;
                }
            }
            return true;
        }

        async function submitForm() {
            const data = getFormData();
            if (!validateFormData(data)) return;

            const submitBtn = document.querySelector('#formMode .submit-btn');
            const originalContent = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="spinner"></div> Analyzing...';

            try {
                const response = await fetch('/predict', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();

                if (result.success) {
                    displayReport(result);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalContent;
            }
        }

        async function submitImage() {
            if (!uploadedImageData) {
                alert('Please select an image');
                return;
            }

            const submitBtn = document.getElementById('imageSubmitBtn');
            const originalContent = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<div class="spinner"></div> Analyzing Image...';

            try {
                const response = await fetch('/predict_from_image', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ image: uploadedImageData })
                });

                const result = await response.json();

                if (result.success) {
                    displayReport(result);
                } else {
                    alert('Error: ' + result.error);
                }
            } catch (error) {
                alert('Error: ' + error.message);
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalContent;
            }
        }

        function displayReport(result) {
            document.getElementById('inputSection').style.display = 'none';
            document.getElementById('reportSection').style.display = 'block';

            const riskCard = document.getElementById('riskCard');
            const riskLevel = document.getElementById('riskLevel');
            const riskScore = document.getElementById('riskScore');

            riskLevel.textContent = result.riskLevel.level;
            riskScore.textContent = result.riskScore + '/100';

            riskCard.className = 'stat-card ' + result.riskLevel.color;

            const parametersGrid = document.getElementById('parametersGrid');
            parametersGrid.innerHTML = '';

            const paramLabels = {
                age: 'Age',
                sex: 'Sex',
                trestbps: 'BP',
                chol: 'Cholesterol',
                thalach: 'Max HR',
                oldpeak: 'Oldpeak',
                ca: 'Vessels',
                fbs: 'FBS'
            };

            for (const [key, label] of Object.entries(paramLabels)) {
                if (result.data[key] !== undefined) {
                    const paramItem = document.createElement('div');
                    paramItem.className = 'param-item';
                    
                    let value = result.data[key];
                    if (key === 'sex') value = value === '1' || value === 1 ? 'Male' : 'Female';
                    if (key === 'fbs') value = value === '1' || value === 1 ? 'High' : 'Normal';
                    if (key === 'trestbps') value += ' mm Hg';
                    if (key === 'chol') value += ' mg/dl';
                    if (key === 'age') value += ' years';
                    
                    paramItem.innerHTML = `
                        <div class="param-label">${label}</div>
                        <div class="param-value">${value}</div>
                    `;
                    parametersGrid.appendChild(paramItem);
                }
            }

            const recommendationsList = document.getElementById('recommendationsList');
            recommendationsList.innerHTML = '';

            result.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.innerHTML = `
                    <span class="check-icon">✓</span>
                    <span>${rec}</span>
                `;
                recommendationsList.appendChild(li);
            });

            document.getElementById('timestamp').textContent = 'Generated on ' + new Date().toLocaleString();
        }

        function resetForm() {
            document.getElementById('inputSection').style.display = 'block';
            document.getElementById('reportSection').style.display = 'none';
            document.getElementById('age').value = '';
            document.getElementById('sex').value = '';
            document.getElementById('cp').value = '';
            document.getElementById('trestbps').value = '';
            document.getElementById('chol').value = '';
            document.getElementById('fbs').value = '';
            document.getElementById('restecg').value = '';
            document.getElementById('thalach').value = '';
            document.getElementById('exang').value = '';
            document.getElementById('oldpeak').value = '';
            document.getElementById('slope').value = '';
            document.getElementById('ca').value = '';
            document.getElementById('thal').value = '';
            document.getElementById('imagePreview').classList.add('hidden');
            document.getElementById('imageInput').value = '';
            document.getElementById('imageSubmitBtn').disabled = true;
            uploadedImageData = null;
        }
    </script>
</body>
</html>
'''

def calculate_risk_score(data):
    """Calculate heart disease risk score based on parameters"""
    score = 0
    
    try:
        age = int(data.get('age', 0))
        if age > 60:
            score += 25
        elif age > 45:
            score += 15
        
        if int(data.get('sex', 0)) == 1:
            score += 10
        
        cp = int(data.get('cp', 0))
        if cp >= 2:
            score += 20
        
        trestbps = int(data.get('trestbps', 0))
        if trestbps > 140:
            score += 15
        
        chol = int(data.get('chol', 0))
        if chol > 240:
            score += 15
        
        if int(data.get('fbs', 0)) == 1:
            score += 10
        
        if int(data.get('exang', 0)) == 1:
            score += 15
        
        oldpeak = float(data.get('oldpeak', 0))
        if oldpeak > 2:
            score += 20
        
        ca = int(data.get('ca', 0))
        if ca > 0:
            score += 25
    except:
        pass
    
    return min(score, 100)

def get_risk_level(score):
    """Determine risk level based on score"""
    if score < 30:
        return {'level': 'Low', 'color': 'low'}
    elif score < 60:
        return {'level': 'Moderate', 'color': 'moderate'}
    else:
        return {'level': 'High', 'color': 'high'}

def generate_recommendations(risk_level, data):
    """Generate health recommendations based on risk and parameters"""
    recommendations = []
    
    if risk_level['level'] == 'High':
        recommendations.append("Consult with a cardiologist immediately for comprehensive evaluation")
        recommendations.append("Consider stress testing and advanced cardiac imaging")
    
    try:
        if int(data.get('chol', 0)) > 240:
            recommendations.append("Focus on cholesterol management through diet and medication")
        
        if int(data.get('trestbps', 0)) > 140:
            recommendations.append("Monitor blood pressure regularly and consider antihypertensive therapy")
        
        if int(data.get('fbs', 0)) == 1:
            recommendations.append("Maintain blood sugar control through diet, exercise, and medication")
    except:
        pass
    
    recommendations.append("Engage in regular moderate-intensity aerobic exercise (150 min/week)")
    recommendations.append("Adopt a heart-healthy diet rich in fruits, vegetables, and whole grains")
    recommendations.append("Schedule regular follow-ups with your healthcare provider")
    
    return recommendations

@app.route('/')
def index():
    """Render the main page"""
    return HTML_TEMPLATE

@app.route('/predict', methods=['POST'])
def predict():
    """Handle prediction request from form"""
    try:
        data = request.get_json()
        
        # Calculate risk
        risk_score = calculate_risk_score(data)
        risk_level = get_risk_level(risk_score)
        recommendations = generate_recommendations(risk_level, data)
        
        return jsonify({
            'success': True,
            'data': data,
            'riskScore': risk_score,
            'riskLevel': risk_level,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/predict_from_image', methods=['POST'])
def predict_from_image():
    """Handle image upload and prediction"""
    try:
        data = request.get_json()
        image_data = data.get('image', '')
        
        # Simulated extraction (In production, use OCR or Claude API)
        # For demonstration, returning sample data
        extracted_data = {
            'age': 55,
            'sex': 1,
            'cp': 2,
            'trestbps': 145,
            'chol': 250,
            'fbs': 1,
            'restecg': 1,
            'thalach': 140,
            'exang': 1,
            'oldpeak': 2.5,
            'slope': 1,
            'ca': 1,
            'thal': 2
        }
        
        # Calculate risk
        risk_score = calculate_risk_score(extracted_data)
        risk_level = get_risk_level(risk_score)
        recommendations = generate_recommendations(risk_level, extracted_data)
        
        return jsonify({
            'success': True,
            'data': extracted_data,
            'riskScore': risk_score,
            'riskLevel': risk_level,
            'recommendations': recommendations
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🫀 HEART HEALTH PREDICTOR - Starting Server")
    print("="*60)
    print("\n📍 Server running at: http://localhost:5000")
    print("📍 Or access via: http://127.0.0.1:5000")
    print("\n✅ Open the URL in your browser to use the application")
    print("⏹️  Press CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)