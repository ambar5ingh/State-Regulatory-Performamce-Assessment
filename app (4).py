import streamlit as st

try:
    import pandas as pd
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    import numpy as np
except ImportError as e:
    st.error(
        f"❌ Missing dependency: **{e}**\n\n"
        "Make sure your `requirements.txt` is in the **same folder** as `app.py` and contains:\n"
        "```\nstreamlit==1.35.0\npandas==2.2.2\nplotly==5.22.0\nnumpy==1.26.4\nwatchdog==4.0.1\n```\n\n"
        "On Streamlit Cloud → **Manage App → Reboot app** after committing the requirements file."
    )
    st.stop()

import json
import os
from datetime import datetime, date

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Regulatory Performance Rating – States & UTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1565c0 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 { margin: 0; font-size: 1.9rem; font-weight: 700; }
    .main-header p  { margin: 0.4rem 0 0; opacity: 0.85; font-size: 0.95rem; }

    .grade-badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 1rem;
        letter-spacing: 0.5px;
    }
    .grade-A { background:#e8f5e9; color:#2e7d32; }
    .grade-B { background:#e3f2fd; color:#1565c0; }
    .grade-C { background:#fff3e0; color:#e65100; }
    .grade-D { background:#fce4ec; color:#b71c1c; }
    .grade-E { background:#f3e5f5; color:#6a1b9a; }

    .metric-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #1a237e; }
    .metric-card .label { font-size: 0.8rem; color: #666; margin-top: 4px; }

    .scorecard-section {
        background: #f8f9fa;
        border-left: 4px solid #1565c0;
        border-radius: 0 8px 8px 0;
        padding: 1rem 1.5rem;
        margin-bottom: 1rem;
    }
    .section-title { font-weight: 700; color: #1a237e; margin-bottom: 0.5rem; }

    div[data-testid="stExpander"] { border: 1px solid #e0e0e0 !important; border-radius: 8px !important; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
    .stDataFrame { border-radius: 8px; overflow: hidden; }
</style>
""", unsafe_allow_html=True)

# ─── DATA ─────────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"

# Baseline scores from the report (FY 2025-26 assessment)
BASELINE_SCORES = {
    "Punjab": {
        "total": 97.0, "grade": "A", "rank": 1,
        "resource_adequacy": 32, "financial_viability": 25, "ease_of_living": 23, "energy_transition": 12, "regulatory_governance": 5,
        "region": "North", "type": "State"
    },
    "Karnataka": {
        "total": 96.0, "grade": "A", "rank": 2,
        "resource_adequacy": 32, "financial_viability": 23, "ease_of_living": 22, "energy_transition": 14, "regulatory_governance": 5,
        "region": "South", "type": "State"
    },
    "Maharashtra": {
        "total": 94.0, "grade": "A", "rank": 3,
        "resource_adequacy": 30, "financial_viability": 22, "ease_of_living": 23, "energy_transition": 14, "regulatory_governance": 5,
        "region": "West", "type": "State"
    },
    "Assam": {
        "total": 93.0, "grade": "A", "rank": 4,
        "resource_adequacy": 32, "financial_viability": 24, "ease_of_living": 20, "energy_transition": 12, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Arunachal Pradesh": {
        "total": 91.0, "grade": "A", "rank": 5,
        "resource_adequacy": 32, "financial_viability": 25, "ease_of_living": 21, "energy_transition": 8, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Madhya Pradesh": {
        "total": 89.0, "grade": "A", "rank": 6,
        "resource_adequacy": 27, "financial_viability": 22, "ease_of_living": 21, "energy_transition": 14, "regulatory_governance": 5,
        "region": "Central", "type": "State"
    },
    "Meghalaya": {
        "total": 89.0, "grade": "A", "rank": 7,
        "resource_adequacy": 32, "financial_viability": 19, "ease_of_living": 20, "energy_transition": 13, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Haryana": {
        "total": 88.5, "grade": "A", "rank": 8,
        "resource_adequacy": 28, "financial_viability": 21, "ease_of_living": 20, "energy_transition": 15, "regulatory_governance": 4.5,
        "region": "North", "type": "State"
    },
    "Himachal Pradesh": {
        "total": 88.0, "grade": "A", "rank": 9,
        "resource_adequacy": 29, "financial_viability": 20, "ease_of_living": 22, "energy_transition": 12, "regulatory_governance": 5,
        "region": "North", "type": "State"
    },
    "Mizoram": {
        "total": 87.0, "grade": "A", "rank": 10,
        "resource_adequacy": 32, "financial_viability": 18, "ease_of_living": 20, "energy_transition": 12, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Jharkhand": {
        "total": 86.67, "grade": "A", "rank": 11,
        "resource_adequacy": 28, "financial_viability": 22, "ease_of_living": 19, "energy_transition": 13, "regulatory_governance": 4.67,
        "region": "East", "type": "State"
    },
    "Sikkim": {
        "total": 78.0, "grade": "B", "rank": 12,
        "resource_adequacy": 24, "financial_viability": 20, "ease_of_living": 18, "energy_transition": 11, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Odisha": {
        "total": 75.5, "grade": "B", "rank": 13,
        "resource_adequacy": 24, "financial_viability": 18, "ease_of_living": 17, "energy_transition": 12, "regulatory_governance": 4.5,
        "region": "East", "type": "State"
    },
    "Chandigarh": {
        "total": 74.0, "grade": "B", "rank": 14,
        "resource_adequacy": 22, "financial_viability": 18, "ease_of_living": 19, "energy_transition": 10, "regulatory_governance": 5,
        "region": "North", "type": "UT"
    },
    "Dadra and Nagar Haveli and Daman and Diu": {
        "total": 74.0, "grade": "B", "rank": 15,
        "resource_adequacy": 22, "financial_viability": 17, "ease_of_living": 19, "energy_transition": 11, "regulatory_governance": 5,
        "region": "West", "type": "UT"
    },
    "Andaman & Nicobar Islands": {
        "total": 72.0, "grade": "B", "rank": 16,
        "resource_adequacy": 28, "financial_viability": 9, "ease_of_living": 16, "energy_transition": 14, "regulatory_governance": 5,
        "region": "Island UT", "type": "UT"
    },
    "Lakshadweep": {
        "total": 72.0, "grade": "B", "rank": 17,
        "resource_adequacy": 26, "financial_viability": 14, "ease_of_living": 17, "energy_transition": 10, "regulatory_governance": 5,
        "region": "Island UT", "type": "UT"
    },
    "Gujarat": {
        "total": 71.0, "grade": "B", "rank": 18,
        "resource_adequacy": 18, "financial_viability": 19, "ease_of_living": 18, "energy_transition": 11, "regulatory_governance": 5,
        "region": "West", "type": "State"
    },
    "Goa": {
        "total": 71.0, "grade": "B", "rank": 19,
        "resource_adequacy": 20, "financial_viability": 17, "ease_of_living": 19, "energy_transition": 10, "regulatory_governance": 5,
        "region": "West", "type": "State"
    },
    "Puducherry": {
        "total": 70.0, "grade": "B", "rank": 20,
        "resource_adequacy": 20, "financial_viability": 17, "ease_of_living": 18, "energy_transition": 10, "regulatory_governance": 5,
        "region": "South", "type": "UT"
    },
    "Uttarakhand": {
        "total": 68.0, "grade": "B", "rank": 21,
        "resource_adequacy": 20, "financial_viability": 16, "ease_of_living": 17, "energy_transition": 10, "regulatory_governance": 5,
        "region": "North", "type": "State"
    },
    "Andhra Pradesh": {
        "total": 63.0, "grade": "C", "rank": 22,
        "resource_adequacy": 10, "financial_viability": 20, "ease_of_living": 13, "energy_transition": 15, "regulatory_governance": 5,
        "region": "South", "type": "State"
    },
    "Ladakh": {
        "total": 63.0, "grade": "C", "rank": 23,
        "resource_adequacy": 22, "financial_viability": 14, "ease_of_living": 15, "energy_transition": 7, "regulatory_governance": 5,
        "region": "North", "type": "UT"
    },
    "Manipur": {
        "total": 62.0, "grade": "C", "rank": 24,
        "resource_adequacy": 20, "financial_viability": 15, "ease_of_living": 14, "energy_transition": 8, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Bihar": {
        "total": 61.0, "grade": "C", "rank": 25,
        "resource_adequacy": 18, "financial_viability": 15, "ease_of_living": 14, "energy_transition": 9, "regulatory_governance": 5,
        "region": "East", "type": "State"
    },
    "Tamil Nadu": {
        "total": 58.0, "grade": "C", "rank": 26,
        "resource_adequacy": 14, "financial_viability": 15, "ease_of_living": 16, "energy_transition": 8, "regulatory_governance": 5,
        "region": "South", "type": "State"
    },
    "Kerala": {
        "total": 55.5, "grade": "C", "rank": 27,
        "resource_adequacy": 14, "financial_viability": 14, "ease_of_living": 15, "energy_transition": 8, "regulatory_governance": 4.5,
        "region": "South", "type": "State"
    },
    "Nagaland": {
        "total": 55.0, "grade": "C", "rank": 28,
        "resource_adequacy": 18, "financial_viability": 13, "ease_of_living": 13, "energy_transition": 6, "regulatory_governance": 5,
        "region": "North-East", "type": "State"
    },
    "Chhattisgarh": {
        "total": 52.0, "grade": "C", "rank": 29,
        "resource_adequacy": 10, "financial_viability": 14, "ease_of_living": 14, "energy_transition": 9, "regulatory_governance": 5,
        "region": "Central", "type": "State"
    },
    "Telangana": {
        "total": 50.5, "grade": "C", "rank": 30,
        "resource_adequacy": 12, "financial_viability": 13, "ease_of_living": 13, "energy_transition": 8, "regulatory_governance": 4.5,
        "region": "South", "type": "State"
    },
    "West Bengal": {
        "total": 50.0, "grade": "C", "rank": 31,
        "resource_adequacy": 14, "financial_viability": 12, "ease_of_living": 12, "energy_transition": 7, "regulatory_governance": 5,
        "region": "East", "type": "State"
    },
    "Jammu & Kashmir": {
        "total": 49.0, "grade": "D", "rank": 32,
        "resource_adequacy": 14, "financial_viability": 12, "ease_of_living": 13, "energy_transition": 7, "regulatory_governance": 3,
        "region": "North", "type": "UT"
    },
    "Uttar Pradesh": {
        "total": 48.0, "grade": "D", "rank": 33,
        "resource_adequacy": 10, "financial_viability": 14, "ease_of_living": 13, "energy_transition": 8, "regulatory_governance": 3,
        "region": "North", "type": "State"
    },
    "Delhi": {
        "total": 40.5, "grade": "D", "rank": 34,
        "resource_adequacy": 8, "financial_viability": 10, "ease_of_living": 12, "energy_transition": 7, "regulatory_governance": 3.5,
        "region": "North", "type": "UT"
    },
    "Rajasthan": {
        "total": 39.0, "grade": "D", "rank": 35,
        "resource_adequacy": 8, "financial_viability": 11, "ease_of_living": 11, "energy_transition": 6, "regulatory_governance": 3,
        "region": "North", "type": "State"
    },
    "Tripura": {
        "total": 21.5, "grade": "E", "rank": 36,
        "resource_adequacy": 5, "financial_viability": 6, "ease_of_living": 6, "energy_transition": 3, "regulatory_governance": 1.5,
        "region": "North-East", "type": "State"
    },
}

MAX_MARKS = {
    "resource_adequacy": 32,
    "financial_viability": 25,
    "ease_of_living": 23,
    "energy_transition": 15,
    "regulatory_governance": 5,
}

PARAMETER_LABELS = {
    "resource_adequacy": "Resource Adequacy (32)",
    "financial_viability": "Financial Viability of DISCOMs (25)",
    "ease_of_living": "Ease of Living / Doing Business (23)",
    "energy_transition": "Energy Transition (15)",
    "regulatory_governance": "Regulatory Governance (5)",
}

GRADE_CONFIG = {
    "A": {"label": "A (≥85)", "color": "#2e7d32", "bg": "#e8f5e9", "min": 85},
    "B": {"label": "B (65–84)", "color": "#1565c0", "bg": "#e3f2fd", "min": 65},
    "C": {"label": "C (50–64)", "color": "#e65100", "bg": "#fff3e0", "min": 50},
    "D": {"label": "D (35–49)", "color": "#b71c1c", "bg": "#fce4ec", "min": 35},
    "E": {"label": "E (<35)",   "color": "#6a1b9a", "bg": "#f3e5f5", "min": 0},
}

def get_grade(score):
    if score >= 85: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "E"

def grade_badge(grade):
    cfg = GRADE_CONFIG[grade]
    return f'<span class="grade-badge grade-{grade}" style="background:{cfg["bg"]};color:{cfg["color"]}">Grade {grade}</span>'

# ─── PERSISTENCE ──────────────────────────────────────────────────────────────
def load_assessments():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    # seed with baseline
    data = {
        "assessments": {},
        "audit_log": []
    }
    entry = {
        "date": "2025-03-31",
        "label": "Baseline – Report FY 2024-25",
        "scores": {k: {p: v[p] for p in list(MAX_MARKS.keys()) + ["total", "grade"]}
                   for k, v in BASELINE_SCORES.items()},
        "notes": "First Report: Rating Regulatory Performance of States and UTs (Power Foundation of India & REC Ltd.)"
    }
    data["assessments"]["2025-03-31"] = entry
    save_assessments(data)
    return data

def save_assessments(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def build_df(scores_dict):
    rows = []
    for state, scores in scores_dict.items():
        base = BASELINE_SCORES.get(state, {})
        rows.append({
            "State/UT": state,
            "Region": base.get("region", "—"),
            "Type": base.get("type", "—"),
            "Resource Adequacy": scores.get("resource_adequacy", 0),
            "Financial Viability": scores.get("financial_viability", 0),
            "Ease of Living": scores.get("ease_of_living", 0),
            "Energy Transition": scores.get("energy_transition", 0),
            "Regulatory Governance": scores.get("regulatory_governance", 0),
            "Total Score": scores.get("total", 0),
            "Grade": scores.get("grade", "E"),
        })
    df = pd.DataFrame(rows).sort_values("Total Score", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def radar_chart(state, scores):
    cats = list(PARAMETER_LABELS.values())
    vals = [
        scores.get("resource_adequacy", 0) / MAX_MARKS["resource_adequacy"] * 100,
        scores.get("financial_viability", 0) / MAX_MARKS["financial_viability"] * 100,
        scores.get("ease_of_living", 0) / MAX_MARKS["ease_of_living"] * 100,
        scores.get("energy_transition", 0) / MAX_MARKS["energy_transition"] * 100,
        scores.get("regulatory_governance", 0) / MAX_MARKS["regulatory_governance"] * 100,
    ]
    fig = go.Figure(go.Scatterpolar(
        r=vals + [vals[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor="rgba(21,101,192,0.15)",
        line=dict(color="#1565c0", width=2),
        name=state,
    ))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100], ticksuffix="%")),
        showlegend=False,
        margin=dict(t=40, b=20, l=40, r=40),
        height=340,
    )
    return fig

# ─── MAIN APP ─────────────────────────────────────────────────────────────────
data = load_assessments()

st.markdown("""
<div class="main-header">
  <h1>⚡ Regulatory Performance Rating – States & Union Territories</h1>
  <p>India Power Sector | Based on: Rating Regulatory Performance Report (Power Foundation of India & REC Ltd.) | Ministry of Power, GoI</p>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/41/Flag_of_India.svg/200px-Flag_of_India.svg.png", width=80)
    st.markdown("### Navigation")
    page = st.radio("", [
        "📊 Dashboard & Rankings",
        "🔍 State/UT Profile",
        "📝 New Assessment Entry",
        "📈 Trend Analysis",
        "⚖️ Compare States/UTs",
        "📋 Assessment History",
    ], label_visibility="collapsed")

    st.markdown("---")
    st.markdown("**Assessment Dates**")
    dates = sorted(data["assessments"].keys(), reverse=True)
    selected_date = st.selectbox("Select Assessment Period", dates, format_func=lambda d: data["assessments"][d]["label"])
    st.caption(f"📅 {selected_date}")

# Get active snapshot
snapshot = data["assessments"][selected_date]
scores = snapshot["scores"]
df = build_df(scores)

# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard & Rankings":
    st.subheader("📊 National Overview")

    # KPI row
    col1, col2, col3, col4, col5 = st.columns(5)
    grade_counts = df["Grade"].value_counts()
    total_states = len(df)
    nat_avg = df["Total Score"].mean()

    with col1:
        st.markdown(f'<div class="metric-card"><div class="value">{total_states}</div><div class="label">States & UTs Assessed</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="metric-card"><div class="value" style="color:#2e7d32">{grade_counts.get("A",0)}</div><div class="label">Grade A (≥ 85 marks)</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="value" style="color:#1565c0">{grade_counts.get("B",0)}</div><div class="label">Grade B (65–84)</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="metric-card"><div class="value" style="color:#e65100">{grade_counts.get("C",0)+grade_counts.get("D",0)+grade_counts.get("E",0)}</div><div class="label">Grade C / D / E (< 65)</div></div>', unsafe_allow_html=True)
    with col5:
        st.markdown(f'<div class="metric-card"><div class="value">{nat_avg:.1f}</div><div class="label">National Average Score</div></div>', unsafe_allow_html=True)

    st.markdown("")

    tab1, tab2, tab3 = st.tabs(["🏆 Rankings Table", "📊 Score Distribution", "🗺️ Parameter Heatmap"])

    with tab1:
        display_df = df.copy()
        display_df["Grade"] = display_df["Grade"].apply(
            lambda g: f"{g} ({'≥85' if g=='A' else '65-84' if g=='B' else '50-64' if g=='C' else '35-49' if g=='D' else '<35'})"
        )
        st.dataframe(
            display_df[["State/UT","Region","Type","Resource Adequacy","Financial Viability","Ease of Living","Energy Transition","Regulatory Governance","Total Score","Grade"]],
            use_container_width=True,
            height=560
        )

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            # Bar chart
            fig_bar = px.bar(
                df.sort_values("Total Score", ascending=True),
                x="Total Score", y="State/UT",
                color="Grade",
                color_discrete_map={"A":"#2e7d32","B":"#1565c0","C":"#e65100","D":"#b71c1c","E":"#6a1b9a"},
                orientation="h",
                title="Score Distribution – All States & UTs",
                labels={"Total Score": "Score (out of 100)"},
                height=700,
            )
            fig_bar.add_vline(x=85, line_dash="dot", line_color="#2e7d32", annotation_text="A")
            fig_bar.add_vline(x=65, line_dash="dot", line_color="#1565c0", annotation_text="B")
            fig_bar.add_vline(x=50, line_dash="dot", line_color="#e65100", annotation_text="C")
            fig_bar.add_vline(x=35, line_dash="dot", line_color="#b71c1c", annotation_text="D")
            fig_bar.update_layout(margin=dict(l=10, r=10))
            st.plotly_chart(fig_bar, use_container_width=True)

        with c2:
            grade_df = grade_counts.reset_index()
            grade_df.columns = ["Grade", "Count"]
            grade_df = grade_df.sort_values("Grade")
            fig_pie = px.pie(
                grade_df, names="Grade", values="Count",
                color="Grade",
                color_discrete_map={"A":"#2e7d32","B":"#1565c0","C":"#e65100","D":"#b71c1c","E":"#6a1b9a"},
                title="Grade Distribution",
                hole=0.4,
            )
            fig_pie.update_traces(textinfo="label+value+percent")
            st.plotly_chart(fig_pie, use_container_width=True)

            # Region-wise avg
            reg_df = df.groupby("Region")["Total Score"].mean().reset_index().sort_values("Total Score", ascending=False)
            fig_reg = px.bar(reg_df, x="Region", y="Total Score",
                             title="Average Score by Region",
                             color="Total Score",
                             color_continuous_scale="Blues")
            st.plotly_chart(fig_reg, use_container_width=True)

    with tab3:
        heat_df = df.set_index("State/UT")[["Resource Adequacy","Financial Viability","Ease of Living","Energy Transition","Regulatory Governance"]].copy()
        # Normalize to %
        heat_norm = heat_df.copy()
        heat_norm["Resource Adequacy"] = heat_df["Resource Adequacy"] / 32 * 100
        heat_norm["Financial Viability"] = heat_df["Financial Viability"] / 25 * 100
        heat_norm["Ease of Living"] = heat_df["Ease of Living"] / 23 * 100
        heat_norm["Energy Transition"] = heat_df["Energy Transition"] / 15 * 100
        heat_norm["Regulatory Governance"] = heat_df["Regulatory Governance"] / 5 * 100

        fig_heat = px.imshow(
            heat_norm.round(1),
            color_continuous_scale="RdYlGn",
            zmin=0, zmax=100,
            aspect="auto",
            title="Parameter-wise Achievement (% of maximum marks)",
            labels=dict(color="Achievement %"),
            height=900
        )
        fig_heat.update_xaxes(tickangle=-25)
        st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 State/UT Profile":
    st.subheader("🔍 State / UT Detailed Profile")
    selected_state = st.selectbox("Select State / UT", sorted(scores.keys()))
    s = scores[selected_state]
    base = BASELINE_SCORES.get(selected_state, {})
    grade = s.get("grade", get_grade(s.get("total", 0)))
    total = s.get("total", 0)

    col1, col2, col3 = st.columns([1.2, 1, 2])
    with col1:
        st.markdown(f"### {selected_state}")
        st.markdown(grade_badge(grade), unsafe_allow_html=True)
        st.markdown(f"**Total Score:** {total} / 100")
        st.markdown(f"**Rank:** {df[df['State/UT']==selected_state].index.tolist()[0] if selected_state in df['State/UT'].values else '—'} of {len(df)}")
        st.markdown(f"**Region:** {base.get('region','—')} | **Type:** {base.get('type','—')}")
    with col2:
        # Gauge
        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total,
            gauge=dict(
                axis=dict(range=[0, 100]),
                steps=[
                    dict(range=[0, 35],   color="#f3e5f5"),
                    dict(range=[35, 50],  color="#fce4ec"),
                    dict(range=[50, 65],  color="#fff3e0"),
                    dict(range=[65, 85],  color="#e3f2fd"),
                    dict(range=[85, 100], color="#e8f5e9"),
                ],
                bar=dict(color="#1565c0"),
                threshold=dict(line=dict(color="red", width=3), thickness=0.75, value=50),
            ),
            title=dict(text="Overall Score"),
            number=dict(suffix="/100"),
        ))
        fig_gauge.update_layout(height=220, margin=dict(t=30, b=0, l=10, r=10))
        st.plotly_chart(fig_gauge, use_container_width=True)
    with col3:
        st.plotly_chart(radar_chart(selected_state, s), use_container_width=True)

    st.markdown("---")
    st.subheader("Parameter Breakdown")
    params = [
        ("resource_adequacy",    "Resource Adequacy",                 32),
        ("financial_viability",  "Financial Viability of DISCOMs",    25),
        ("ease_of_living",       "Ease of Living / Doing Business",   23),
        ("energy_transition",    "Energy Transition",                 15),
        ("regulatory_governance","Regulatory Governance",              5),
    ]
    for key, label, max_m in params:
        val = s.get(key, 0)
        pct = val / max_m * 100
        color = "#2e7d32" if pct >= 85 else "#1565c0" if pct >= 65 else "#e65100" if pct >= 50 else "#b71c1c"
        st.markdown(f"""
        <div class="scorecard-section">
          <div class="section-title">{label}</div>
          <div style="display:flex;align-items:center;gap:1rem">
            <div style="font-size:1.4rem;font-weight:700;color:{color};min-width:90px">{val} / {max_m}</div>
            <div style="flex:1;background:#e0e0e0;border-radius:8px;height:14px">
              <div style="width:{pct:.1f}%;background:{color};height:14px;border-radius:8px;transition:width 0.4s"></div>
            </div>
            <div style="min-width:50px;text-align:right;color:{color};font-weight:600">{pct:.1f}%</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # History of this state across assessments
    history = []
    for d, snap in sorted(data["assessments"].items()):
        if selected_state in snap["scores"]:
            history.append({
                "Date": d,
                "Assessment": snap["label"],
                "Total Score": snap["scores"][selected_state].get("total", 0),
                "Grade": snap["scores"][selected_state].get("grade", "—"),
            })
    if len(history) > 1:
        st.markdown("---")
        st.subheader("📈 Score History")
        hist_df = pd.DataFrame(history)
        fig_hist = px.line(hist_df, x="Date", y="Total Score", markers=True,
                           title=f"Score Trend – {selected_state}",
                           labels={"Total Score": "Score (out of 100)"})
        fig_hist.update_traces(line=dict(color="#1565c0", width=2.5), marker=dict(size=9))
        fig_hist.add_hline(y=85, line_dash="dot", line_color="#2e7d32", annotation_text="Grade A")
        fig_hist.add_hline(y=65, line_dash="dot", line_color="#1565c0", annotation_text="Grade B")
        fig_hist.add_hline(y=50, line_dash="dot", line_color="#e65100", annotation_text="Grade C")
        st.plotly_chart(fig_hist, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 New Assessment Entry":
    st.subheader("📝 Enter New Periodic Assessment")
    st.info("Enter updated scores for a new assessment cycle. Scores are automatically saved and become available in all charts and trend views.")

    with st.form("new_assessment"):
        col1, col2 = st.columns(2)
        with col1:
            assess_date = st.date_input("Assessment Date", value=date.today(), max_value=date.today())
        with col2:
            assess_label = st.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27 / True-up FY 2024-25")

        assess_notes = st.text_area("Notes / Remarks", placeholder="Key changes, data source, policy updates...")

        st.markdown("---")
        st.markdown("#### Enter Scores for Each State / UT")
        st.caption("Leave a state unchanged to carry forward its previous score automatically.")

        state_list = sorted(BASELINE_SCORES.keys())
        prev_scores = snapshot["scores"]
        new_scores = {}

        for state in state_list:
            prev = prev_scores.get(state, {})
            with st.expander(f"📍 {state}  ·  Previous: {prev.get('total',0):.1f}  ·  Grade {prev.get('grade','—')}"):
                c1, c2, c3, c4, c5 = st.columns(5)
                ra  = c1.number_input("Resource Adequacy (0-32)",  0.0, 32.0, float(prev.get("resource_adequacy", 0)),  0.5, key=f"{state}_ra")
                fv  = c2.number_input("Fin. Viability (0-25)",     0.0, 25.0, float(prev.get("financial_viability", 0)), 0.5, key=f"{state}_fv")
                el  = c3.number_input("Ease of Living (0-23)",     0.0, 23.0, float(prev.get("ease_of_living", 0)),      0.5, key=f"{state}_el")
                et  = c4.number_input("Energy Transition (0-15)",  0.0, 15.0, float(prev.get("energy_transition", 0)),   0.5, key=f"{state}_et")
                rg  = c5.number_input("Reg. Governance (0-5)",     0.0, 5.0,  float(prev.get("regulatory_governance", 0)), 0.5, key=f"{state}_rg")
                total = ra + fv + el + et + rg
                grade = get_grade(total)
                st.markdown(f"**Computed Total: {total:.2f} / 100 → {grade}**")
                new_scores[state] = {
                    "resource_adequacy": ra,
                    "financial_viability": fv,
                    "ease_of_living": el,
                    "energy_transition": et,
                    "regulatory_governance": rg,
                    "total": round(total, 2),
                    "grade": grade,
                }

        submitted = st.form_submit_button("💾 Save Assessment", use_container_width=True, type="primary")
        if submitted:
            if not assess_label.strip():
                st.error("Please provide an assessment label.")
            else:
                date_key = str(assess_date)
                data["assessments"][date_key] = {
                    "date": date_key,
                    "label": assess_label,
                    "scores": new_scores,
                    "notes": assess_notes,
                }
                data["audit_log"].append({
                    "action": "new_assessment",
                    "date": date_key,
                    "label": assess_label,
                    "timestamp": datetime.now().isoformat(),
                })
                save_assessments(data)
                st.success(f"✅ Assessment '{assess_label}' saved for {date_key}!")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trend Analysis":
    st.subheader("📈 Trend Analysis Across Assessment Cycles")

    if len(data["assessments"]) < 2:
        st.warning("At least 2 assessment periods are needed for trend analysis. Add a new assessment via the '📝 New Assessment Entry' page.")
    else:
        all_dates = sorted(data["assessments"].keys())
        all_states = sorted(BASELINE_SCORES.keys())

        filter_states = st.multiselect("Select States/UTs to compare", all_states,
                                       default=["Punjab","Karnataka","Maharashtra","Uttar Pradesh","Delhi","Tripura"])

        trend_rows = []
        for d in all_dates:
            snap = data["assessments"][d]
            for state in filter_states:
                if state in snap["scores"]:
                    trend_rows.append({
                        "Date": d,
                        "Assessment": snap["label"],
                        "State/UT": state,
                        "Total Score": snap["scores"][state].get("total", 0),
                        "Grade": snap["scores"][state].get("grade", "—"),
                        "Resource Adequacy": snap["scores"][state].get("resource_adequacy", 0),
                        "Financial Viability": snap["scores"][state].get("financial_viability", 0),
                        "Ease of Living": snap["scores"][state].get("ease_of_living", 0),
                        "Energy Transition": snap["scores"][state].get("energy_transition", 0),
                        "Regulatory Governance": snap["scores"][state].get("regulatory_governance", 0),
                    })

        if trend_rows:
            trend_df = pd.DataFrame(trend_rows)

            fig_trend = px.line(trend_df, x="Date", y="Total Score", color="State/UT",
                                markers=True, title="Total Score Trend",
                                labels={"Total Score": "Score (out of 100)"})
            for threshold, label, color in [(85,"Grade A","#2e7d32"),(65,"Grade B","#1565c0"),
                                             (50,"Grade C","#e65100"),(35,"Grade D","#b71c1c")]:
                fig_trend.add_hline(y=threshold, line_dash="dot", line_color=color,
                                    annotation_text=label, annotation_position="right")
            st.plotly_chart(fig_trend, use_container_width=True)

            # Parameter trends
            st.markdown("#### Parameter-wise Trends")
            param_sel = st.selectbox("Select Parameter", ["Resource Adequacy","Financial Viability","Ease of Living","Energy Transition","Regulatory Governance"])
            fig_param = px.line(trend_df, x="Date", y=param_sel, color="State/UT",
                                markers=True, title=f"{param_sel} – Trend")
            st.plotly_chart(fig_param, use_container_width=True)

            # Change table
            if len(all_dates) >= 2:
                st.markdown("#### Score Change (First vs Latest Assessment)")
                first_d, last_d = all_dates[0], all_dates[-1]
                changes = []
                for state in all_states:
                    s1 = data["assessments"][first_d]["scores"].get(state, {})
                    s2 = data["assessments"][last_d]["scores"].get(state, {})
                    if s1 and s2:
                        delta = round(s2.get("total", 0) - s1.get("total", 0), 2)
                        changes.append({
                            "State/UT": state,
                            f"Score ({first_d})": s1.get("total", 0),
                            f"Score ({last_d})": s2.get("total", 0),
                            "Change (Δ)": delta,
                            "Direction": "▲ Improved" if delta > 0 else "▼ Declined" if delta < 0 else "→ No Change",
                        })
                chg_df = pd.DataFrame(changes).sort_values("Change (Δ)", ascending=False)
                st.dataframe(chg_df, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare States/UTs":
    st.subheader("⚖️ Side-by-Side Comparison")

    col1, col2 = st.columns(2)
    with col1:
        state_a = st.selectbox("State / UT A", sorted(scores.keys()), index=0)
    with col2:
        state_b = st.selectbox("State / UT B", sorted(scores.keys()), index=1)

    if state_a == state_b:
        st.warning("Please select two different states.")
    else:
        sa, sb = scores[state_a], scores[state_b]
        bA, bB = BASELINE_SCORES.get(state_a, {}), BASELINE_SCORES.get(state_b, {})

        # Summary
        c1, c2 = st.columns(2)
        with c1:
            g = sa.get("grade","E")
            st.markdown(f'<div class="metric-card"><div class="value" style="color:{GRADE_CONFIG[g]["color"]}">{sa.get("total",0)}</div><div class="label">{state_a} · {grade_badge(g)}</div></div>', unsafe_allow_html=True)
        with c2:
            g = sb.get("grade","E")
            st.markdown(f'<div class="metric-card"><div class="value" style="color:{GRADE_CONFIG[g]["color"]}">{sb.get("total",0)}</div><div class="label">{state_b} · {grade_badge(g)}</div></div>', unsafe_allow_html=True)

        st.markdown("")

        # Radar overlay
        cats = list(PARAMETER_LABELS.values())
        vals_a = [sa.get("resource_adequacy",0)/32*100, sa.get("financial_viability",0)/25*100,
                  sa.get("ease_of_living",0)/23*100, sa.get("energy_transition",0)/15*100,
                  sa.get("regulatory_governance",0)/5*100]
        vals_b = [sb.get("resource_adequacy",0)/32*100, sb.get("financial_viability",0)/25*100,
                  sb.get("ease_of_living",0)/23*100, sb.get("energy_transition",0)/15*100,
                  sb.get("regulatory_governance",0)/5*100]

        fig_cmp = go.Figure()
        for vals, name, color in [(vals_a, state_a, "#1565c0"), (vals_b, state_b, "#e65100")]:
            fig_cmp.add_trace(go.Scatterpolar(
                r=vals + [vals[0]], theta=cats + [cats[0]],
                fill="toself", name=name,
                fillcolor=color.replace("#","rgba(").replace("1565c0","21,101,192,0.12)").replace("e65100","230,81,0,0.12)"),
                line=dict(color=color, width=2)
            ))
        fig_cmp.update_layout(polar=dict(radialaxis=dict(range=[0,100], ticksuffix="%")),
                               legend=dict(orientation="h", y=-0.15), height=420)
        st.plotly_chart(fig_cmp, use_container_width=True)

        # Table
        params_compare = [
            ("Resource Adequacy", "resource_adequacy", 32),
            ("Financial Viability", "financial_viability", 25),
            ("Ease of Living", "ease_of_living", 23),
            ("Energy Transition", "energy_transition", 15),
            ("Regulatory Governance", "regulatory_governance", 5),
            ("**Total Score**", "total", 100),
        ]
        cmp_rows = []
        for label, key, mx in params_compare:
            va = sa.get(key, 0)
            vb = sb.get(key, 0)
            winner = f"✅ {state_a}" if va > vb else (f"✅ {state_b}" if vb > va else "Tied")
            cmp_rows.append({"Parameter": label, state_a: f"{va} / {mx}", state_b: f"{vb} / {mx}", "Better": winner})
        st.table(pd.DataFrame(cmp_rows))


# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 Assessment History":
    st.subheader("📋 Assessment History & Audit Log")

    st.markdown("#### All Saved Assessments")
    hist_rows = []
    for d, snap in sorted(data["assessments"].items(), reverse=True):
        sc = snap["scores"]
        avg = np.mean([v.get("total",0) for v in sc.values()]) if sc else 0
        hist_rows.append({
            "Date": d,
            "Label": snap["label"],
            "States Covered": len(sc),
            "National Avg Score": round(avg, 2),
            "Notes": snap.get("notes", "")[:60] + "..." if len(snap.get("notes","")) > 60 else snap.get("notes",""),
        })
    st.dataframe(pd.DataFrame(hist_rows), use_container_width=True)

    if data["audit_log"]:
        st.markdown("#### Audit Log")
        audit_df = pd.DataFrame(data["audit_log"])
        st.dataframe(audit_df, use_container_width=True)

    st.markdown("---")
    st.markdown("#### Delete Assessment")
    del_options = [d for d in sorted(data["assessments"].keys()) if d != "2025-03-31"]
    if del_options:
        del_sel = st.selectbox("Select assessment to delete (baseline cannot be deleted)", del_options)
        if st.button("🗑️ Delete Selected Assessment", type="secondary"):
            del data["assessments"][del_sel]
            save_assessments(data)
            st.success(f"Deleted assessment: {del_sel}")
            st.rerun()
    else:
        st.info("Only the baseline assessment exists. Add new assessments to see options here.")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:0.8rem'>"
    "Based on: <b>First Report – Rating Regulatory Performance of States & UTs</b> | "
    "Power Foundation of India (PFI) &amp; REC Ltd. | Ministry of Power, GoI | "
    "Assessment Parameters: Electricity Act 2003, MoP Rules, APTEL Judgments"
    "</div>",
    unsafe_allow_html=True
)
