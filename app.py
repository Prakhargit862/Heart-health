from flask import Flask, request, render_template_string, jsonify
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio
import plotly.graph_objects as go
import datetime
import traceback

app = Flask(__name__)

# -----------------------
# Configuration / load
# -----------------------
MODEL_FILE = "heart_health_model.pkl"
FEATURE_ORDER = [
    "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
    "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]

# Load model safely
model = None
try:
    model = joblib.load(MODEL_FILE)
    print(f"Loaded model: {MODEL_FILE}")
except Exception as e:
    print(f"Error loading model '{MODEL_FILE}': {e}")
    traceback.print_exc()

# In-memory prediction history
# Each item: {"time": str, "features": dict, "pred": int, "prob": float or None}
PRED_HISTORY = []

# -----------------------
# Base Styling
# -----------------------
base_style = """<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
body{margin:0;padding:0;font-family:'Inter',sans-serif;background:linear-gradient(120deg,#5b86e5,#36d1dc);min-height:100vh;color:#2d3748;}
.navbar{background:rgba(255,255,255,0.95);padding:1.2rem 2rem;display:flex;justify-content:space-between;align-items:center;border-bottom:3px solid #5b86e5;box-shadow:0 4px 30px rgba(0,0,0,0.08);position:sticky;top:0;z-index:1000}
.navbar h2{color:#5b86e5;font-weight:700;font-size:1.25rem}
.navbar a{color:#4a5568;text-decoration:none;margin-left:16px;font-weight:600}
.hero{text-align:center;padding:2.2rem 1rem;color:white}
.hero h1{font-size:2.4rem;margin-bottom:0.2rem}
.container{max-width:1100px;background:white;margin:1.6rem auto;padding:1.8rem;border-radius:14px;box-shadow:0 20px 60px rgba(0,0,0,0.12)}
.grid-3{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;margin-top:1rem}
.card{background:#fff;padding:1rem;border-radius:12px;box-shadow:0 10px 25px rgba(0,0,0,0.06);border-left:6px solid #5b86e5}
.stat-large{font-size:1.6rem;font-weight:700;color:#2d3748}
.stat-label{color:#6b7280;margin-top:6px;font-weight:600}
.form-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:0.9rem;margin-top:1rem}
.form-group label{display:block;margin-bottom:6px;font-weight:700;color:#374151}
.form-group input{width:100%;padding:10px;border-radius:8px;border:1.5px solid #e6eefc;font-size:0.95rem}
button{background:linear-gradient(135deg,#5b86e5 0%,#36d1dc 100%);color:white;padding:12px 16px;border:none;border-radius:10px;cursor:pointer;font-weight:700;margin-top:10px}
.chart-row{display:grid;grid-template-columns:2fr 1fr;gap:1rem;margin-top:1rem}
.chart-wrapper{background:#fafbfd;padding:0.7rem;border-radius:10px;border:1px solid #eef5ff}
.small{font-size:0.9rem;color:#6b7280}
.footer{color:white;text-align:center;padding:1rem;margin-top:1rem}
.history-table{width:100%;border-collapse:collapse;margin-top:0.6rem}
.history-table th, .history-table td{padding:6px;border-bottom:1px solid #f1f5f9;font-size:0.92rem;text-align:left}
@media(max-width:880px){.chart-row{grid-template-columns:1fr}}
</style>"""

# -------------------------
# Helpers
# -------------------------
def get_features_from_form(req_form):
    feature_list = []
    feature_dict = {}
    errors = []
    for fname in FEATURE_ORDER:
        val = req_form.get(fname)
        if val is None or str(val).strip() == "":
            errors.append(f"Missing field: {fname}")
            feature_list.append(0.0)
            feature_dict[fname] = 0.0
        else:
            try:
                v = float(val)
                feature_list.append(v)
                feature_dict[fname] = v
            except:
                errors.append(f"Invalid numeric value for {fname}: '{val}'")
                feature_list.append(0.0)
                feature_dict[fname] = 0.0
    return feature_list, feature_dict, errors

def history_to_dataframe_for_trend():
    """Return DataFrame with time (datetime) and prob (0-1). If no history, return None."""
    if not PRED_HISTORY:
        return None
    rows = []
    for item in PRED_HISTORY:
        t = item.get("time")
        try:
            dt = datetime.datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
        except:
            dt = datetime.datetime.now()
        prob = item.get("prob")
        if prob is None:
            # If probability not present, use pred as 0/1
            prob = float(item.get("pred", 0))
        rows.append({"time": dt, "prob": prob})
    df = pd.DataFrame(rows).sort_values("time")
    return df

# -------------------------
# Home route (form)
# -------------------------
@app.route("/", methods=["GET"])
def home():
    defaults = {"age": 54, "sex": 1, "cp": 1, "trestbps": 130, "chol": 246, "fbs": 0,
                "restecg": 0, "thalach": 150, "exang": 0, "oldpeak": 1.0, "slope": 2, "ca": 0, "thal": 2}
    form_html = ""
    for fname in FEATURE_ORDER:
        label = fname.replace("_", " ").title()
        form_html += f"""
        <div class="form-group">
            <label>{label}</label>
            <input type="number" step="any" name="{fname}" value="{defaults.get(fname, '')}" required>
        </div>
        """

    recent_rows = ""
    for h in PRED_HISTORY[-6:][::-1]:
        prob_display = f"{round(h['prob']*100,1)}%" if h['prob'] is not None else "N/A"
        recent_rows += f"<tr><td>{h['time']}</td><td>{int(h['features'].get('age',0))}</td><td>{'High' if h['pred']==1 else 'Low'}</td><td>{prob_display}</td></tr>"

    page = f"""
    <!doctype html><html><head><title>Heart Health AI Clinic</title>{base_style}</head><body>
    <div class="navbar"><h2>❤️ Heart Health AI Clinic</h2><div><a href="/">Home</a><a href="/dashboard">Analytics</a></div></div>
    <div class="hero"><h1>AI-Powered Cardiac Risk Assessment</h1><p class="small">Enter patient features to get an AI-assisted risk assessment.</p></div>

    <div class="container">
      <div class="grid-3">
        <div class="card">
          <div class="stat-large">{len(PRED_HISTORY)}</div>
          <div class="stat-label">Total Assessments</div>
        </div>
        <div class="card">
          <div class="stat-large">{round((sum([h['prob'] for h in PRED_HISTORY if h['prob'] is not None]) / len([h for h in PRED_HISTORY if h['prob'] is not None]))*100,1) if PRED_HISTORY and any(h['prob'] is not None for h in PRED_HISTORY) else 'N/A'}</div>
          <div class="stat-label">Average Risk (%)</div>
        </div>
        <div class="card">
          <div class="stat-large">{('High' if PRED_HISTORY and PRED_HISTORY[-1]['pred']==1 else ('Low' if PRED_HISTORY else 'N/A'))}</div>
          <div class="stat-label">Last Prediction</div>
        </div>
      </div>

      <div style="margin-top:1rem" class="card">
        <h3>Patient Assessment Form</h3>
        <form method="POST" action="/predict">
            <div class="form-grid">{form_html}</div>
            <button type="submit">🔍 Analyze Cardiac Risk</button>
        </form>
      </div>

      <div style="margin-top:1rem" class="card">
        <h4>Recent Predictions</h4>
        <table class="history-table"><thead><tr><th>Time</th><th>Age</th><th>Pred</th><th>Prob</th></tr></thead><tbody>
        {recent_rows if recent_rows else '<tr><td colspan="4" class="small">No predictions yet — make an assessment to populate history.</td></tr>'}
        </tbody></table>
      </div>
    </div>

    <div class="footer">© 2025 Heart Health AI Clinic — Designed by Prakhar</div>
    </body></html>
    """
    return render_template_string(page)

# -------------------------
# Predict route
# -------------------------
@app.route("/predict", methods=["POST"])
def predict():
    try:
        feature_list, feature_dict, errors = get_features_from_form(request.form)
        if errors:
            return render_template_string(f"{base_style}<div class='container'><h3>Input Errors</h3><ul>" +
                                          "".join([f"<li>{e}</li>" for e in errors]) + "</ul><a href='/'><button>Go Back</button></a></div>")
        X_df = pd.DataFrame([dict(zip(FEATURE_ORDER, feature_list))])

        # Try DataFrame prediction first
        try:
            pred = int(model.predict(X_df)[0])
        except Exception:
            arr = np.array(feature_list).reshape(1, -1)
            pred = int(model.predict(arr)[0])

        # Try predict_proba if available
        prob = None
        try:
            prob = float(model.predict_proba(X_df)[0][1])
        except Exception:
            try:
                prob = float(model.predict_proba(np.array(feature_list).reshape(1, -1))[0][1])
            except Exception:
                prob = None

        # add to history
        hist_item = {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "features": X_df.iloc[0].to_dict(),
            "pred": pred,
            "prob": prob
        }
        PRED_HISTORY.append(hist_item)
        if len(PRED_HISTORY) > 500:
            PRED_HISTORY.pop(0)

        # prepare result text and gauge
        prob_pct = round(prob*100,1) if prob is not None else None
        result_text = "High Risk Detected" if pred==1 else "Low Risk Profile"
        css_class = "high" if pred==1 else "low"
        rec = "Immediate clinical review recommended." if pred==1 else "Maintain healthy lifestyle; routine check-ups."

        gauge_html = ""
        if prob is not None:
            gauge = go.Figure(go.Indicator(
                mode="gauge+number",
                value=prob_pct,
                title={'text': "Predicted Risk (%)"},
                gauge={'axis':{'range':[0,100]}, 'bar':{'color': "#b71c1c" if prob_pct>=50 else "#256029"},
                       'steps':[{'range':[0,40],'color':'#d4fc79'},{'range':[40,70],'color':'#fff3cc'},{'range':[70,100],'color':'#ffe6e6'}]}
            ))
            gauge.update_layout(margin=dict(l=10,r=10,t=30,b=10), template="plotly_white", height=250)
            gauge_html = pio.to_html(gauge, full_html=False)

        # render results page
        page = f"""
        <!doctype html><html><head><title>Results - Heart Health AI</title>{base_style}</head><body>
        <div class="navbar"><h2>❤️ Heart Health AI Clinic</h2><div><a href="/">Home</a><a href="/dashboard">Analytics</a></div></div>
        <div class="hero"><h1>Assessment Result</h1><p class="small">AI-assisted clinical guidance (not a definitive diagnosis).</p></div>

        <div class="container">
          <div class="grid-3">
            <div class="card"><div class="stat-large">{result_text}</div><div class="stat-label">Result</div></div>
            <div class="card"><div class="stat-large">{prob_pct if prob_pct is not None else 'N/A'}</div><div class="stat-label">Predicted Risk (%)</div></div>
            <div class="card"><div class="stat-large">{hist_item['time']}</div><div class="stat-label">Assessment Time</div></div>
          </div>

          <div style="margin-top:1rem" class="card">
            <h4>Patient Summary</h4>
            <p class="small">""" + " | ".join([f"<strong>{k}:</strong> {v}" for k,v in hist_item['features'].items()]) + """</p>
            <div style="margin-top:10px" class="small"><strong>Clinical recommendation:</strong> """ + rec + """</div>
          </div>

          <div class="chart-row">
            <div class="chart-wrapper">{gauge_html}</div>
            <div class="card">
              <h4>Recent Predictions</h4>
              <table class="history-table"><thead><tr><th>Time</th><th>Pred</th><th>Prob</th></tr></thead><tbody>
              {"".join([f"<tr><td>{h['time']}</td><td>{'High' if h['pred']==1 else 'Low'}</td><td>{(str(round(h['prob']*100,1))+'%' if h['prob'] is not None else 'N/A')}</td></tr>" for h in PRED_HISTORY[-8:][::-1]])}
              </tbody></table>
            </div>
          </div>

          <div style="margin-top:1rem" class="card">
            <h4>Trend: Predicted Risk Over Time</h4>
            {make_trend_html()}
          </div>

          <a href="/"><button style="margin-top:12px">🔄 New Assessment</button></a>
          <a href="/dashboard"><button style="background:linear-gradient(135deg,#48bb78,#38a169);margin-top:12px">📊 Open Dashboard</button></a>

        </div>
        <div class="footer">© 2025 Heart Health AI Clinic — For demonstration only</div>
        </body></html>
        """
        return render_template_string(page)
    except Exception as e:
        tb = traceback.format_exc()
        return render_template_string(f"{base_style}<div class='container'><h3>Unexpected error</h3><pre>{tb}</pre><a href='/'><button>Go back</button></a></div>")

# -------------------------
# Trend helper (uses PRED_HISTORY or simulated demo)
# -------------------------
def make_trend_html():
    # If we have history with probs -> use it, else simulate
    df = history_to_dataframe_for_trend()
    if df is None or df.empty:
        # simulate
        now = datetime.datetime.now()
        times = [now - datetime.timedelta(minutes=10*i) for i in range(12)][::-1]
        probs = np.clip(np.random.normal(0.35, 0.18, len(times)), 0, 1)
        df = pd.DataFrame({"time": times, "prob": probs})

    # create plotly line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["time"], y=(df["prob"]*100), mode="lines+markers", line=dict(color="#5b86e5"), name="Pred Risk %"))
    fig.update_layout(template="plotly_white", xaxis_title="Time", yaxis_title="Risk (%)", margin=dict(t=30,b=20,l=30,r=10), height=300)
    return pio.to_html(fig, full_html=False)

# -------------------------
# Dashboard route
# -------------------------
@app.route("/dashboard")
def dashboard():
    # build demo dataset or a summary of PRED_HISTORY
    if PRED_HISTORY:
        hist_df = history_to_dataframe_for_trend()
        df = pd.DataFrame({
            "age": np.random.randint(29, 78, 220),
            "chol": np.random.randint(126, 564, 220),
            "thalach": np.random.randint(70, 200, 220),
            "bp": np.random.randint(90, 180, 220),
        })
    else:
        # simulated
        np.random.seed(42)
        df = pd.DataFrame({
            "age": np.random.randint(29, 78, 220),
            "chol": np.random.randint(126, 564, 220),
            "thalach": np.random.randint(70, 200, 220),
            "bp": np.random.randint(90, 180, 220),
        })
    df["risk"] = ((df["age"] > 55) & (df["thalach"] < 140)) | (df["chol"] > 240)
    df["risk"] = df["risk"].astype(int)

    fig1 = px.scatter(df, x="age", y="chol", color="risk", size="thalach", title="Cholesterol vs Age (size=MaxHR)",
                      color_discrete_map={0:"#48bb78",1:"#f56565"})
    fig2 = px.histogram(df, x="thalach", color="risk", title="Max Heart Rate Distribution",
                        color_discrete_map={0:"#667eea",1:"#f56565"}, barmode="overlay")
    fig3 = px.box(df, x="risk", y="thalach", color="risk", title="MaxHR by Risk", color_discrete_map={0:"#48bb78",1:"#f56565"})
    fig4 = go.Figure(data=[go.Pie(labels=["Low Risk","High Risk"], values=[(df['risk']==0).sum(), (df['risk']==1).sum()], marker=dict(colors=["#48bb78","#f56565"]), hole=0.4)])
    charts_html = "".join([f"<div class='chart-wrapper'>{pio.to_html(fig, full_html=False)}</div>" for fig in [fig1, fig2, fig3, fig4]])

    html = f"""
    <!doctype html><html><head><title>Analytics Dashboard</title>{base_style}</head><body>
    <div class="navbar"><h2>📊 Clinical Analytics</h2><div><a href="/">Home</a><a href="/dashboard">Analytics</a></div></div>
    <div class="hero"><h1>Cardiovascular Data Intelligence</h1><p class="small">Interactive insights to support clinical care</p></div>
    <div class="container">{charts_html}</div>
    <div class="footer">© 2025 Heart Health AI Clinic — For demo</div>
    </body></html>
    """
    return render_template_string(html)

# -------------------------
# API endpoints
# -------------------------
@app.route("/api/history")
def api_history():
    return jsonify(PRED_HISTORY[::-1])

@app.route("/api/health")
def api_health():
    return jsonify({"status":"ok","model_loaded": model is not None})

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(debug=True)
