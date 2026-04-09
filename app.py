"""
Regulatory Performance Rating — States & UTs
Power Foundation of India & REC Ltd. | Ministry of Power, GoI
Improved UI/UX version
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
import os
from datetime import datetime, date
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Regulatory Performance — States & UTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #f0f4f8 !important;
    color: #1a1a2e !important;
}
.stApp { background-color: #f0f4f8 !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b4b 0%, #1a3a7c 60%, #0f5499 100%) !important;
    border-right: none !important;
}
[data-testid="stSidebar"] * { color: #ffffff !important; font-family: 'IBM Plex Sans', sans-serif !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: 13px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.22) !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.1) !important;
    color: #fff !important;
    border-color: rgba(255,255,255,0.25) !important;
}
[data-testid="stSidebarCollapseButton"] button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
    border-radius: 50% !important;
    color: #fff !important;
}
[data-testid="stSidebarCollapseButton"] button svg { fill: #fff !important; }
[data-testid="collapsedControl"] button {
    background: #1a3a7c !important;
    border: 1px solid #0d1b4b !important;
    border-radius: 50% !important;
}
[data-testid="collapsedControl"] button svg { fill: #fff !important; }

/* ── Cards & Metrics ── */
.metric-card {
    background: #ffffff;
    border: 0.5px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    text-align: center;
    box-shadow: 0 1px 8px rgba(13,27,75,0.06);
    transition: transform 0.15s, box-shadow 0.15s;
    margin-bottom: 4px;
}
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 4px 16px rgba(13,27,75,0.12); }
.metric-card .metric-val {
    font-family: 'Playfair Display', serif;
    font-size: 2rem; font-weight: 800; line-height: 1; margin-bottom: 4px;
}
.metric-card .metric-lbl {
    font-size: 0.66rem; color: #64748b; text-transform: uppercase;
    letter-spacing: 0.8px; font-weight: 500;
}
.metric-card .metric-sub { font-size: 0.72rem; color: #94a3b8; margin-top: 2px; }

/* ── Header ── */
.page-header {
    background: linear-gradient(135deg, #0d1b4b 0%, #1a3a7c 55%, #0f5499 100%);
    padding: 1.5rem 1.75rem 1.25rem;
    border-radius: 14px;
    margin-bottom: 1.25rem;
    position: relative;
    overflow: hidden;
    border: none;
}
.page-header::before {
    content: '';
    position: absolute; right: -40px; top: -40px;
    width: 180px; height: 180px;
    border: 28px solid rgba(255,255,255,0.05);
    border-radius: 50%;
}
.page-header h1 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.5rem !important; font-weight: 800 !important;
    color: #ffffff !important; margin: 0 0 4px 0 !important;
}
.page-header .sub { font-size: 0.77rem; color: rgba(255,255,255,0.65); margin: 0; }
.header-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }
.header-tag {
    background: rgba(255,255,255,0.12); border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.68rem; color: rgba(255,255,255,0.88); font-weight: 500;
}

/* ── Grade Badges ── */
.badge { display: inline-block; padding: 3px 13px; border-radius: 20px; font-weight: 600; font-size: 0.78rem; }
.badge-A { background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7; }
.badge-B { background: #e3f2fd; color: #0d47a1; border: 1px solid #90caf9; }
.badge-C { background: #fff3e0; color: #bf360c; border: 1px solid #ffcc80; }
.badge-D { background: #fce4ec; color: #880e4f; border: 1px solid #f48fb1; }
.badge-E { background: #f3e5f5; color: #4a148c; border: 1px solid #ce93d8; }

/* ── Rank List ── */
.rank-item {
    display: flex; align-items: center; gap: 10px;
    padding: 8px 12px; border-radius: 8px; margin-bottom: 3px;
    transition: background 0.12s;
}
.rank-item:hover { background: #f8fafc; }
.rank-num { font-size: 0.7rem; color: #94a3b8; width: 24px; text-align: right; font-weight: 500; }
.rank-name { font-size: 0.84rem; font-weight: 500; flex: 1; color: #1a1a2e; }
.rank-meta { font-size: 0.67rem; color: #94a3b8; }

/* ── Param Bars ── */
.param-block { margin-bottom: 0.85rem; }
.param-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 5px; }
.param-name { font-size: 0.79rem; font-weight: 500; color: #475569; }
.param-score { font-size: 0.79rem; font-weight: 600; color: #1a1a2e; }
.param-pct { font-size: 0.72rem; color: #94a3b8; }
.param-track { height: 7px; background: #e2e8f0; border-radius: 4px; overflow: hidden; }
.param-fill { height: 100%; border-radius: 4px; transition: width 0.6s ease; }

/* ── Alert Box ── */
.alert-box {
    border-left: 4px solid #1a3a7c; background: #eff6ff;
    border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 6px 0;
    font-size: 0.83rem; color: #1a1a2e;
}
.alert-box strong { font-weight: 600; }

/* ── Section Titles ── */
.section-title {
    font-size: 0.67rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 1.5px; color: #64748b;
    padding-bottom: 8px; border-bottom: 1.5px solid #e2e8f0;
    margin-bottom: 14px;
}

/* ── Profile Score ── */
.profile-score {
    font-family: 'Playfair Display', serif;
    font-size: 3.5rem; font-weight: 800; line-height: 1; text-align: center;
}
.profile-rank { font-size: 0.77rem; color: #64748b; text-align: center; margin-top: 4px; }

/* ── Compare Card ── */
.cmp-card {
    background: #ffffff; border: 0.5px solid #e2e8f0;
    border-radius: 12px; padding: 1.25rem; text-align: center;
    box-shadow: 0 1px 8px rgba(0,0,0,0.05);
}
.cmp-score {
    font-family: 'Playfair Display', serif;
    font-size: 3rem; font-weight: 800; line-height: 1;
}

/* ── Heatmap Cell ── */
.hm-cell {
    display: inline-block; padding: 4px 8px; border-radius: 5px;
    font-size: 0.72rem; font-weight: 500; min-width: 42px; text-align: center;
}

/* ── Table ── */
.stDataFrame { border-radius: 10px; overflow: hidden; border: 0.5px solid #e2e8f0 !important; }
thead { background: #f8fafc; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-weight: 500 !important; font-size: 13px !important;
    color: #475569 !important;
}
.stTabs [aria-selected="true"] { color: #0d1b4b !important; }
.stTabs [data-baseweb="tab-border"] { background: #0d1b4b !important; }

/* ── Select/Input ── */
[data-baseweb="select"] > div, [data-baseweb="input"] > div {
    border-color: #e2e8f0 !important; border-radius: 8px !important;
    background: #ffffff !important;
}
[data-baseweb="select"] span { color: #1a1a2e !important; }

/* ── Misc ── */
#MainMenu, footer, header { visibility: hidden; }
.stDownloadButton button {
    background: #0d1b4b !important; color: #fff !important;
    font-weight: 500 !important; border-radius: 8px !important; border: none !important;
}
p, span, div, li, label { color: #1a1a2e !important; }
[data-testid="stMetricValue"], [data-testid="stMetricLabel"] { color: #1a1a2e !important; }
</style>
""", unsafe_allow_html=True)


# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"

GRADE_COLOR = {"A": "#1b5e20", "B": "#0d47a1", "C": "#bf360c", "D": "#880e4f", "E": "#4a148c"}
GRADE_BG    = {"A": "#e8f5e9", "B": "#e3f2fd", "C": "#fff3e0", "D": "#fce4ec", "E": "#f3e5f5"}
GRADE_BORDER= {"A": "#a5d6a7","B": "#90caf9", "C": "#ffcc80", "D": "#f48fb1", "E": "#ce93d8"}

PARAM_META = [
    {"key": "ra", "label": "Resource Adequacy",     "max": 32, "color": "#185FA5"},
    {"key": "fv", "label": "Financial Viability",   "max": 25, "color": "#1b5e20"},
    {"key": "el", "label": "Ease of Living",        "max": 23, "color": "#bf360c"},
    {"key": "et", "label": "Energy Transition",     "max": 15, "color": "#BA7517"},
    {"key": "rg", "label": "Regulatory Governance", "max": 5,  "color": "#4a148c"},
]

BASELINE = {
    "Punjab":               {"ra":32,"fv":25,"el":23,"et":12,"rg":5,   "total":97.0,  "grade":"A","region":"North",      "type":"State"},
    "Karnataka":            {"ra":32,"fv":23,"el":22,"et":14,"rg":5,   "total":96.0,  "grade":"A","region":"South",      "type":"State"},
    "Maharashtra":          {"ra":30,"fv":22,"el":23,"et":14,"rg":5,   "total":94.0,  "grade":"A","region":"West",       "type":"State"},
    "Assam":                {"ra":32,"fv":24,"el":20,"et":12,"rg":5,   "total":93.0,  "grade":"A","region":"North-East", "type":"State"},
    "Arunachal Pradesh":    {"ra":32,"fv":25,"el":21,"et":8, "rg":5,   "total":91.0,  "grade":"A","region":"North-East", "type":"State"},
    "Madhya Pradesh":       {"ra":27,"fv":22,"el":21,"et":14,"rg":5,   "total":89.0,  "grade":"A","region":"Central",    "type":"State"},
    "Meghalaya":            {"ra":32,"fv":19,"el":20,"et":13,"rg":5,   "total":89.0,  "grade":"A","region":"North-East", "type":"State"},
    "Haryana":              {"ra":28,"fv":21,"el":20,"et":15,"rg":4.5, "total":88.5,  "grade":"A","region":"North",      "type":"State"},
    "Himachal Pradesh":     {"ra":29,"fv":20,"el":22,"et":12,"rg":5,   "total":88.0,  "grade":"A","region":"North",      "type":"State"},
    "Mizoram":              {"ra":32,"fv":18,"el":20,"et":12,"rg":5,   "total":87.0,  "grade":"A","region":"North-East", "type":"State"},
    "Jharkhand":            {"ra":28,"fv":22,"el":19,"et":13,"rg":4.67,"total":86.67, "grade":"A","region":"East",       "type":"State"},
    "Sikkim":               {"ra":24,"fv":20,"el":18,"et":11,"rg":5,   "total":78.0,  "grade":"B","region":"North-East", "type":"State"},
    "Odisha":               {"ra":24,"fv":18,"el":17,"et":12,"rg":4.5, "total":75.5,  "grade":"B","region":"East",       "type":"State"},
    "Chandigarh":           {"ra":22,"fv":18,"el":19,"et":10,"rg":5,   "total":74.0,  "grade":"B","region":"North",      "type":"UT"},
    "Dadra & NH and DD":    {"ra":22,"fv":17,"el":19,"et":11,"rg":5,   "total":74.0,  "grade":"B","region":"West",       "type":"UT"},
    "Andaman & Nicobar":    {"ra":28,"fv":9, "el":16,"et":14,"rg":5,   "total":72.0,  "grade":"B","region":"Island UT",  "type":"UT"},
    "Lakshadweep":          {"ra":26,"fv":14,"el":17,"et":10,"rg":5,   "total":72.0,  "grade":"B","region":"Island UT",  "type":"UT"},
    "Gujarat":              {"ra":18,"fv":19,"el":18,"et":11,"rg":5,   "total":71.0,  "grade":"B","region":"West",       "type":"State"},
    "Goa":                  {"ra":20,"fv":17,"el":19,"et":10,"rg":5,   "total":71.0,  "grade":"B","region":"West",       "type":"State"},
    "Puducherry":           {"ra":20,"fv":17,"el":18,"et":10,"rg":5,   "total":70.0,  "grade":"B","region":"South",      "type":"UT"},
    "Uttarakhand":          {"ra":20,"fv":16,"el":17,"et":10,"rg":5,   "total":68.0,  "grade":"B","region":"North",      "type":"State"},
    "Andhra Pradesh":       {"ra":10,"fv":20,"el":13,"et":15,"rg":5,   "total":63.0,  "grade":"C","region":"South",      "type":"State"},
    "Ladakh":               {"ra":22,"fv":14,"el":15,"et":7, "rg":5,   "total":63.0,  "grade":"C","region":"North",      "type":"UT"},
    "Manipur":              {"ra":20,"fv":15,"el":14,"et":8, "rg":5,   "total":62.0,  "grade":"C","region":"North-East", "type":"State"},
    "Bihar":                {"ra":18,"fv":15,"el":14,"et":9, "rg":5,   "total":61.0,  "grade":"C","region":"East",       "type":"State"},
    "Tamil Nadu":           {"ra":14,"fv":15,"el":16,"et":8, "rg":5,   "total":58.0,  "grade":"C","region":"South",      "type":"State"},
    "Kerala":               {"ra":14,"fv":14,"el":15,"et":8, "rg":4.5, "total":55.5,  "grade":"C","region":"South",      "type":"State"},
    "Nagaland":             {"ra":18,"fv":13,"el":13,"et":6, "rg":5,   "total":55.0,  "grade":"C","region":"North-East", "type":"State"},
    "Chhattisgarh":         {"ra":10,"fv":14,"el":14,"et":9, "rg":5,   "total":52.0,  "grade":"C","region":"Central",    "type":"State"},
    "Telangana":            {"ra":12,"fv":13,"el":13,"et":8, "rg":4.5, "total":50.5,  "grade":"C","region":"South",      "type":"State"},
    "West Bengal":          {"ra":14,"fv":12,"el":12,"et":7, "rg":5,   "total":50.0,  "grade":"C","region":"East",       "type":"State"},
    "Jammu & Kashmir":      {"ra":14,"fv":12,"el":13,"et":7, "rg":3,   "total":49.0,  "grade":"D","region":"North",      "type":"UT"},
    "Uttar Pradesh":        {"ra":10,"fv":14,"el":13,"et":8, "rg":3,   "total":48.0,  "grade":"D","region":"North",      "type":"State"},
    "Delhi":                {"ra":8, "fv":10,"el":12,"et":7, "rg":3.5, "total":40.5,  "grade":"D","region":"North",      "type":"UT"},
    "Rajasthan":            {"ra":8, "fv":11,"el":11,"et":6, "rg":3,   "total":39.0,  "grade":"D","region":"North",      "type":"State"},
    "Tripura":              {"ra":5, "fv":6, "el":6, "et":3, "rg":1.5, "total":21.5,  "grade":"E","region":"North-East", "type":"State"},
}

_FONT   = "IBM Plex Sans, sans-serif"
_LAYOUT = dict(paper_bgcolor="#ffffff", plot_bgcolor="#ffffff",
               font=dict(family=_FONT, color="#1a1a2e", size=12),
               margin=dict(l=10, r=10, t=40, b=10))


# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_grade(score: float) -> str:
    if score >= 85: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "E"

def gv(s: dict, *keys):
    for k in keys:
        if k in s: return s[k]
    return 0

def badge_html(grade: str, label: str = None) -> str:
    txt = label or f"Grade {grade}"
    return f'<span class="badge badge-{grade}">{txt}</span>'

def score_bar_html(pct: float, color: str, height: int = 7) -> str:
    return (f'<div class="param-track">'
            f'<div class="param-fill" style="width:{min(pct,100):.1f}%;background:{color};height:{height}px"></div>'
            f'</div>')

def grade_color(g: str) -> str:
    return GRADE_COLOR.get(g, "#555")

def score_to_color(s: float) -> str:
    g = get_grade(s)
    return grade_color(g)


# ─── PERSISTENCE ──────────────────────────────────────────────────────────────
def load_data() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    scores = {
        st: {"ra": b["ra"], "fv": b["fv"], "el": b["el"], "et": b["et"],
             "rg": b["rg"], "total": b["total"], "grade": b["grade"]}
        for st, b in BASELINE.items()
    }
    data = {
        "assessments": {
            "2025-03-31": {
                "date": "2025-03-31",
                "label": "Baseline — Report FY 2024-25",
                "scores": scores,
                "notes": "First Report: Rating Regulatory Performance of States & UTs"
            }
        },
        "audit_log": []
    }
    save_data(data)
    return data

def save_data(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def build_df(scores: dict) -> pd.DataFrame:
    rows = []
    for state, s in scores.items():
        b = BASELINE.get(state, {})
        rows.append({
            "State/UT":          state,
            "Region":            b.get("region", "—"),
            "Type":              b.get("type", "—"),
            "Res. Adequacy":     gv(s, "ra", "resource_adequacy"),
            "Fin. Viability":    gv(s, "fv", "financial_viability"),
            "Ease of Living":    gv(s, "el", "ease_of_living"),
            "Energy Transition": gv(s, "et", "energy_transition"),
            "Reg. Governance":   gv(s, "rg", "regulatory_governance"),
            "Total":             round(s.get("total", 0), 2),
            "Grade":             s.get("grade", "E"),
        })
    df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

def make_csv_template() -> bytes:
    rows = [{"State/UT": st, "Resource Adequacy": b["ra"], "Financial Viability": b["fv"],
             "Ease of Living": b["el"], "Energy Transition": b["et"],
             "Regulatory Governance": b["rg"]}
            for st, b in BASELINE.items()]
    return pd.DataFrame(rows).to_csv(index=False).encode()

def parse_csv_upload(file) -> dict | None:
    try:
        xdf = pd.read_csv(file)
        xdf.columns = xdf.columns.str.strip()
        col_map = {"Resource Adequacy": "ra", "Financial Viability": "fv",
                   "Ease of Living": "el", "Energy Transition": "et",
                   "Regulatory Governance": "rg"}
        state_col = next((c for c in xdf.columns if "state" in c.lower() or "ut" in c.lower()), None)
        if state_col is None:
            return None
        scores = {}
        for _, row in xdf.iterrows():
            state = str(row[state_col]).strip()
            if not state or state.lower() == "nan":
                continue
            rec = {}
            for full, short in col_map.items():
                matched = next((c for c in xdf.columns if full.lower() in c.lower()), None)
                rec[short] = float(row[matched]) if matched and pd.notna(row[matched]) else 0.0
            rec["total"] = round(sum(rec.values()), 2)
            rec["grade"] = get_grade(rec["total"])
            scores[state] = rec
        return scores if scores else None
    except Exception as e:
        st.error(f"File parsing error: {e}")
        return None


# ─── PLOTLY HELPERS ───────────────────────────────────────────────────────────
def apply_theme(fig, height=400, margin=None, showlegend=False, legend=None):
    mg = margin or dict(l=50, r=20, t=40, b=40)
    fig.update_layout(
        **_LAYOUT,
        height=height,
        showlegend=showlegend,
        margin=mg,
        legend=legend or {},
    )

def style_axes(fig, xtitle="", ytitle="", gridcolor="#f1f5f9"):
    xkw = dict(gridcolor=gridcolor, linecolor="#e2e8f0", color="#475569",
               tickfont=dict(family=_FONT, size=11), automargin=True)
    if xtitle:
        xkw["title_text"] = xtitle
        xkw["title_font"] = dict(color="#475569", family=_FONT)
    fig.update_xaxes(**xkw)
    ykw = dict(gridcolor=gridcolor, linecolor="#e2e8f0", color="#475569",
               tickfont=dict(family=_FONT, size=11), automargin=True)
    if ytitle:
        ykw["title_text"] = ytitle
        ykw["title_font"] = dict(color="#475569", family=_FONT)
    fig.update_yaxes(**ykw)


def chart_rankings(df_sorted: pd.DataFrame) -> go.Figure:
    colors = [GRADE_COLOR[g] + "cc" for g in df_sorted["Grade"]]
    fig = go.Figure(go.Bar(
        x=df_sorted["Total"],
        y=df_sorted["State/UT"],
        orientation="h",
        marker_color=colors,
        marker_line_color=[GRADE_COLOR[g] for g in df_sorted["Grade"]],
        marker_line_width=1.5,
        marker_cornerradius=4,
        text=[f"{v:.1f}" for v in df_sorted["Total"]],
        textposition="outside",
        textfont=dict(size=10, family=_FONT, color="#475569"),
        hovertemplate="<b>%{y}</b><br>Score: %{x}<extra></extra>",
    ))
    for threshold, color, label in [
        (85, GRADE_COLOR["A"], "A threshold"),
        (65, GRADE_COLOR["B"], "B threshold"),
        (50, GRADE_COLOR["C"], "C threshold"),
        (35, GRADE_COLOR["D"], "D threshold"),
    ]:
        fig.add_vline(x=threshold, line_dash="dot", line_color=color,
                      line_width=1.5, opacity=0.7)
    apply_theme(fig, height=max(500, len(df_sorted) * 23),
                margin=dict(l=10, r=60, t=40, b=20))
    style_axes(fig, xtitle="Score (out of 100)")
    fig.update_xaxes(range=[0, 115])
    fig.update_yaxes(autorange="reversed")
    return fig


def chart_grade_donut(gc: pd.Series) -> go.Figure:
    grades = list(gc.index)
    fig = go.Figure(go.Pie(
        labels=[f"Grade {g}" for g in grades],
        values=gc.values,
        hole=0.62,
        marker=dict(
            colors=[GRADE_BG[g] for g in grades],
            line=dict(color=[GRADE_COLOR[g] for g in grades], width=2),
        ),
        textinfo="label+value",
        textfont=dict(size=11, family=_FONT),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>",
    ))
    apply_theme(fig, height=300, margin=dict(l=10, r=10, t=30, b=10))
    return fig


def chart_region_bar(df: pd.DataFrame) -> go.Figure:
    palette = ["#185FA5", "#1b5e20", "#bf360c", "#BA7517", "#4a148c", "#0F6E56", "#D85A30"]
    rdf = df.groupby("Region")["Total"].mean().sort_values(ascending=False).reset_index()
    fig = go.Figure(go.Bar(
        x=rdf["Region"],
        y=rdf["Total"].round(1),
        marker_color=[palette[i % len(palette)] + "bb" for i in range(len(rdf))],
        marker_line_color=[palette[i % len(palette)] for i in range(len(rdf))],
        marker_line_width=1.5,
        marker_cornerradius=5,
        text=rdf["Total"].round(1),
        textposition="outside",
        textfont=dict(size=10, family=_FONT),
        hovertemplate="<b>%{x}</b><br>Avg Score: %{y:.1f}<extra></extra>",
    ))
    apply_theme(fig, height=300, margin=dict(l=40, r=20, t=30, b=40))
    style_axes(fig, ytitle="Average Score")
    fig.update_yaxes(range=[0, 110])
    fig.update_xaxes(tickangle=-20)
    return fig


def chart_heatmap_plotly(df: pd.DataFrame) -> go.Figure:
    param_keys   = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
    param_maxes  = [32, 25, 23, 15, 5]
    heat = df.set_index("State/UT")[param_keys].copy()
    for col, mx in zip(param_keys, param_maxes):
        heat[col] = (heat[col] / mx * 100).round(1)
    fig = go.Figure(go.Heatmap(
        z=heat.values,
        x=param_keys,
        y=heat.index.tolist(),
        colorscale=[[0, "#fce4ec"], [0.35, "#fff3e0"], [0.6, "#e3f2fd"], [1.0, "#e8f5e9"]],
        zmin=0, zmax=100,
        text=[[f"{v:.0f}%" for v in row] for row in heat.values],
        texttemplate="%{text}",
        textfont=dict(size=9, family=_FONT, color="#1a1a2e"),
        colorbar=dict(
            title=dict(text="% of Max", font=dict(family=_FONT, size=11, color="#475569")),
            tickfont=dict(family=_FONT, size=10, color="#475569"),
        ),
        hovertemplate="<b>%{y}</b><br>%{x}: %{text}<extra></extra>",
    ))
    apply_theme(fig, height=max(600, len(heat) * 20),
                margin=dict(l=10, r=120, t=30, b=80))
    style_axes(fig)
    fig.update_yaxes(autorange="reversed")
    fig.update_xaxes(tickangle=-25)
    return fig


def chart_scatter(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        df, x="Fin. Viability", y="Res. Adequacy",
        size="Total", color="Grade",
        color_discrete_map=GRADE_COLOR,
        hover_name="State/UT",
        hover_data={"Total": True, "Grade": True},
        size_max=40,
    )
    apply_theme(fig, height=460, margin=dict(l=60, r=20, t=30, b=50),
                showlegend=True,
                legend=dict(bgcolor="#ffffff", bordercolor="#e2e8f0", borderwidth=1,
                            font=dict(family=_FONT, size=11)))
    style_axes(fig, xtitle="Financial Viability (out of 25)", ytitle="Resource Adequacy (out of 32)")
    return fig


def chart_type_box(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for typ, color in [("State", "#185FA5"), ("UT", "#bf360c")]:
        vals = df[df["Type"] == typ]["Total"].tolist()
        fig.add_trace(go.Box(
            y=vals, name=typ, marker_color=color,
            boxpoints="all", jitter=0.4, pointpos=0,
            line=dict(color=color, width=2),
            fillcolor=color + "22",
            hovertemplate=f"<b>{typ}</b><br>Score: %{{y}}<extra></extra>",
        ))
    apply_theme(fig, height=340, margin=dict(l=50, r=20, t=30, b=30), showlegend=False)
    style_axes(fig, ytitle="Total Score")
    fig.update_yaxes(range=[0, 110])
    return fig


def chart_radar(state_name: str, vals: list, maxes: list, color: str) -> go.Figure:
    labels = [p["label"] for p in PARAM_META]
    pcts   = [v / m * 100 for v, m in zip(vals, maxes)]
    fig = go.Figure(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=labels + [labels[0]],
        fill="toself",
        fillcolor=color + "33",
        line=dict(color=color, width=2.5),
        name=state_name,
        hovertemplate="<b>%{theta}</b><br>%{r:.1f}%<extra></extra>",
    ))
    apply_theme(fig, height=350, margin=dict(l=40, r=40, t=30, b=40))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100],
                                   tickfont=dict(size=9, family=_FONT),
                                   gridcolor="#e2e8f0"),
                   angularaxis=dict(tickfont=dict(size=10, family=_FONT))))
    return fig


def chart_compare_radar(sa: str, va: dict, sb: str, vb: dict) -> go.Figure:
    keys   = [p["key"] for p in PARAM_META]
    maxes  = [p["max"] for p in PARAM_META]
    labels = [p["label"] for p in PARAM_META]
    fig = go.Figure()
    for name, v, color, dash in [(sa, va, "#185FA5", None), (sb, vb, "#bf360c", "dot")]:
        pcts = [v[k] / m * 100 for k, m in zip(keys, maxes)]
        fig.add_trace(go.Scatterpolar(
            r=pcts + [pcts[0]], theta=labels + [labels[0]],
            fill="toself", fillcolor=color + "22",
            line=dict(color=color, width=2.5, dash=dash or "solid"),
            name=name,
            hovertemplate=f"<b>{name}</b><br>%{{theta}}: %{{r:.1f}}%<extra></extra>",
        ))
    apply_theme(fig, height=420, margin=dict(l=40, r=40, t=30, b=60),
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.18,
                            font=dict(family=_FONT, size=11)))
    fig.update_layout(
        polar=dict(radialaxis=dict(range=[0, 100], tickvals=[25, 50, 75, 100],
                                   tickfont=dict(size=9, family=_FONT),
                                   gridcolor="#e2e8f0"),
                   angularaxis=dict(tickfont=dict(size=10, family=_FONT))))
    return fig


def chart_trend(tdf: pd.DataFrame, param: str) -> go.Figure:
    palette = ["#185FA5","#1b5e20","#bf360c","#BA7517","#4a148c","#0F6E56","#D85A30","#4e342e"]
    fig = go.Figure()
    for i, (state, grp) in enumerate(tdf.groupby("State/UT")):
        grp = grp.sort_values("Date")
        fig.add_trace(go.Scatter(
            x=grp["Date"], y=grp[param], mode="lines+markers", name=state,
            line=dict(color=palette[i % len(palette)], width=2.5),
            marker=dict(size=8, symbol="circle"),
            hovertemplate=f"<b>{state}</b><br>%{{x}}<br>{param}: %{{y}}<extra></extra>",
        ))
    apply_theme(fig, height=420, showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=-0.3,
                            font=dict(family=_FONT, size=10),
                            bgcolor="#ffffff", bordercolor="#e2e8f0", borderwidth=1))
    style_axes(fig, ytitle=param)
    return fig


def chart_delta(chg_df: pd.DataFrame) -> go.Figure:
    chg_df = chg_df.sort_values("Δ")
    colors = [GRADE_COLOR["A"] + "cc" if v >= 0 else GRADE_COLOR["D"] + "cc" for v in chg_df["Δ"]]
    fig = go.Figure(go.Bar(
        x=chg_df["State/UT"], y=chg_df["Δ"],
        marker_color=colors,
        marker_cornerradius=4,
        hovertemplate="<b>%{x}</b><br>Δ: %{y}<extra></extra>",
    ))
    fig.add_hline(y=0, line_color="#94a3b8", line_width=1)
    apply_theme(fig, height=380)
    style_axes(fig, ytitle="Δ Score")
    fig.update_xaxes(tickangle=-40, tickfont=dict(size=10))
    return fig


# ─── LOAD DATA ────────────────────────────────────────────────────────────────
data = load_data()


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1.2rem 0 0.6rem'>
      <div style='font-size:2.2rem'>⚡</div>
      <div style='font-family:"Playfair Display",serif;font-size:1.05rem;font-weight:700;
                  color:#fff;margin-top:4px'>Regulatory Performance</div>
      <div style='font-size:0.72rem;color:rgba(255,255,255,0.55);margin-top:3px'>
        States & Union Territories</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    page = st.radio("Navigate", [
        "📊 Overview",
        "🏆 Rankings",
        "🔍 State Profile",
        "⚖️ Compare",
        "🗺️ Heatmap",
        "📈 Trends",
        "📤 Upload",
        "📝 New Assessment",
        "📋 History",
    ], label_visibility="collapsed")

    st.markdown("---")

    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox(
        "Assessment Period",
        dates,
        format_func=lambda d: data["assessments"][d]["label"],
    )

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.68rem;color:rgba(255,255,255,0.45);text-align:center;line-height:1.6'>
      Power Foundation of India<br>REC Ltd. | Ministry of Power<br>Government of India
    </div>""", unsafe_allow_html=True)


snapshot = data["assessments"][sel_date]
scores   = snapshot["scores"]
df       = build_df(scores)
all_states = sorted(scores.keys())


# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
  <h1>⚡ Regulatory Performance Rating — States &amp; UTs</h1>
  <p class="sub">Power Foundation of India &amp; REC Ltd. | Ministry of Power, Government of India</p>
  <div class="header-tags">
    <span class="header-tag">Resource Adequacy</span>
    <span class="header-tag">Financial Viability</span>
    <span class="header-tag">Ease of Living</span>
    <span class="header-tag">Energy Transition</span>
    <span class="header-tag">Regulatory Governance</span>
  </div>
</div>""", unsafe_allow_html=True)


# ─── KPI STRIP ────────────────────────────────────────────────────────────────
gc   = df["Grade"].value_counts()
avg  = df["Total"].mean()
n    = len(df)

kc1, kc2, kc3, kc4, kc5, kc6 = st.columns(6)
kpi_data = [
    (str(n),             "#0d1b4b", "States & UTs",    ""),
    (str(gc.get("A",0)), GRADE_COLOR["A"], "Grade A",  "≥ 85 marks"),
    (str(gc.get("B",0)), GRADE_COLOR["B"], "Grade B",  "65–84 marks"),
    (str(gc.get("C",0)), GRADE_COLOR["C"], "Grade C",  "50–64 marks"),
    (str(gc.get("D",0)+gc.get("E",0)), GRADE_COLOR["D"], "Grade D/E", "< 50 marks"),
    (f"{avg:.1f}",       "#64748b", "National Avg",    "out of 100"),
]
for col, (val, color, lbl, sub) in zip([kc1,kc2,kc3,kc4,kc5,kc6], kpi_data):
    with col:
        st.markdown(
            f"<div class='metric-card'>"
            f"<div class='metric-val' style='color:{color}'>{val}</div>"
            f"<div class='metric-lbl'>{lbl}</div>"
            f"{'<div class=\"metric-sub\">'+sub+'</div>' if sub else ''}"
            f"</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Overview":
    sorted_df = df.sort_values("Total", ascending=False)
    top5   = sorted_df.head(5)
    bot5   = sorted_df.tail(5)

    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.markdown("<div class='section-title'>Grade Distribution</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_grade_donut(gc), use_container_width=True)

    with col_r:
        st.markdown("<div class='section-title'>Average Score by Region</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_region_bar(df), use_container_width=True)

    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.markdown("<div class='section-title'>States vs Union Territories</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_type_box(df), use_container_width=True)

    with col_b:
        st.markdown("<div class='section-title'>Resource Adequacy vs Financial Viability</div>", unsafe_allow_html=True)
        st.plotly_chart(chart_scatter(df), use_container_width=True)

    st.markdown("<div class='section-title'>Top 5 Performers</div>", unsafe_allow_html=True)
    for _, row in top5.iterrows():
        pct = row["Total"]
        st.markdown(
            f"<div class='rank-item'>"
            f"<span class='rank-num'>#{row.name}</span>"
            f"{badge_html(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<div style='display:flex;align-items:center;gap:8px;min-width:160px'>"
            f"{score_bar_html(pct, grade_color(row['Grade']))}"
            f"<span style='font-size:0.82rem;font-weight:600;color:{grade_color(row[\"Grade\"])};min-width:36px'>{pct:.1f}</span>"
            f"</div></div>", unsafe_allow_html=True)

    st.markdown("<br><div class='section-title'>Bottom 5 Performers</div>", unsafe_allow_html=True)
    for _, row in bot5.iterrows():
        pct = row["Total"]
        st.markdown(
            f"<div class='rank-item'>"
            f"<span class='rank-num'>#{row.name}</span>"
            f"{badge_html(row['Grade'])}"
            f"<div style='flex:1'><div class='rank-name'>{row['State/UT']}</div>"
            f"<div class='rank-meta'>{row['Region']} · {row['Type']}</div></div>"
            f"<span style='font-size:0.82rem;font-weight:600;color:{grade_color(row[\"Grade\"])}'>{pct:.1f}</span>"
            f"</div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  RANKINGS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🏆 Rankings":
    fc1, fc2, fc3 = st.columns([3, 1, 1])
    search      = fc1.text_input("Search", placeholder="Filter by name…", label_visibility="collapsed")
    filter_type = fc2.selectbox("Type", ["All", "State", "UT"], label_visibility="collapsed")
    filter_grade= fc3.selectbox("Grade", ["All", "A", "B", "C", "D", "E"], label_visibility="collapsed")

    fdf = df.copy()
    if search:       fdf = fdf[fdf["State/UT"].str.contains(search, case=False)]
    if filter_type  != "All": fdf = fdf[fdf["Type"]  == filter_type]
    if filter_grade != "All": fdf = fdf[fdf["Grade"] == filter_grade]

    st.plotly_chart(chart_rankings(fdf.sort_values("Total", ascending=True)), use_container_width=True)

    st.markdown("<div class='section-title'>Detailed Table</div>", unsafe_allow_html=True)
    disp = fdf.copy()
    disp.insert(0, "Rank", disp.index)
    styled = disp.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100)
    st.dataframe(styled, use_container_width=True, hide_index=True)
    st.download_button(
        "⬇️ Download CSV",
        fdf.to_csv(index=False).encode(),
        "regulatory_rankings.csv",
        mime="text/csv",
    )


# ══════════════════════════════════════════════════════════════════════════════
#  STATE PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 State Profile":
    sel = st.selectbox(
        "Select State / UT",
        sorted(scores.keys()),
        format_func=lambda s: f"{s}  ·  Grade {scores[s].get('grade','?')}  ·  {scores[s].get('total',0):.1f}",
    )
    s_data = scores[sel]
    b_data = BASELINE.get(sel, {})
    vals   = {p["key"]: gv(s_data, p["key"]) for p in PARAM_META}
    total  = s_data.get("total", 0)
    grade  = s_data.get("grade", get_grade(total))
    rank   = df[df["State/UT"] == sel].index.tolist()
    rank   = rank[0] if rank else "—"

    show_peers = st.checkbox("Show regional peers", value=False)

    col_left, col_right = st.columns([1, 2])
    with col_left:
        st.markdown(
            f"<div style='background:#fff;border:0.5px solid #e2e8f0;border-radius:14px;"
            f"padding:1.5rem;text-align:center;box-shadow:0 1px 8px rgba(0,0,0,0.05)'>"
            f"<div style='font-family:\"Playfair Display\",serif;font-size:1.25rem;"
            f"font-weight:700;color:#1a1a2e'>{sel}</div>"
            f"<div style='margin:10px 0'>{badge_html(grade)}</div>"
            f"<div style='font-size:0.75rem;color:#94a3b8;margin-bottom:8px'>"
            f"Rank <strong style='color:#1a1a2e'>#{rank}</strong> of {len(df)}</div>"
            f"<div class='profile-score' style='color:{grade_color(grade)}'>{total:.1f}</div>"
            f"<div class='profile-rank'>out of 100</div>"
            f"<hr style='border-color:#e2e8f0;margin:12px 0'>"
            f"<div style='font-size:0.76rem;color:#64748b'>"
            f"🗺️ {b_data.get('region','—')} &nbsp;|&nbsp; 🏛️ {b_data.get('type','—')}</div>"
            f"</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Hero metrics
        hc1, hc2, hc3 = st.columns(3)
        with hc1:
            st.markdown(
                f"<div class='metric-card'><div class='metric-val' style='font-size:1.3rem;"
                f"color:{grade_color(grade)}'>{total:.0f}%</div>"
                f"<div class='metric-lbl'>Overall</div></div>", unsafe_allow_html=True)
        with hc2:
            st.markdown(
                f"<div class='metric-card'><div class='metric-val' style='font-size:1.3rem;"
                f"color:#1a1a2e'>#{rank}</div>"
                f"<div class='metric-lbl'>National</div></div>", unsafe_allow_html=True)
        with hc3:
            region_rank = (
                sorted([s for s in scores if BASELINE.get(s, {}).get("region") == b_data.get("region")],
                       key=lambda s: scores[s].get("total", 0), reverse=True).index(sel) + 1
                if sel in scores else "—"
            )
            st.markdown(
                f"<div class='metric-card'><div class='metric-val' style='font-size:1.3rem;"
                f"color:#1a1a2e'>#{region_rank}</div>"
                f"<div class='metric-lbl'>Region</div></div>", unsafe_allow_html=True)

        st.markdown("<br><div class='section-title'>Parameter Breakdown</div>", unsafe_allow_html=True)
        for p in PARAM_META:
            v   = vals[p["key"]]
            pct = v / p["max"] * 100
            st.markdown(
                f"<div class='param-block'>"
                f"<div class='param-header'>"
                f"<span class='param-name'>{p['label']}</span>"
                f"<span class='param-score'>{v} / {p['max']} "
                f"<span class='param-pct'>({pct:.0f}%)</span></span>"
                f"</div>"
                f"{score_bar_html(pct, p['color'])}"
                f"</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown("<div class='section-title'>Parameter Radar</div>", unsafe_allow_html=True)
        st.plotly_chart(
            chart_radar(sel, [vals[p["key"]] for p in PARAM_META],
                        [p["max"] for p in PARAM_META], grade_color(grade)),
            use_container_width=True)

        if show_peers:
            region = b_data.get("region", "")
            peers  = df[df["Region"] == region].sort_values("Total", ascending=False)
            st.markdown(f"<div class='section-title'>Regional Peers — {region}</div>", unsafe_allow_html=True)
            for _, row in peers.iterrows():
                is_sel = row["State/UT"] == sel
                bg = "#eff6ff" if is_sel else "transparent"
                st.markdown(
                    f"<div class='rank-item' style='background:{bg};border-radius:8px'>"
                    f"<span class='rank-num'>#{row.name}</span>"
                    f"{badge_html(row['Grade'])}"
                    f"<div class='rank-name' style='font-weight:{600 if is_sel else 400}'>"
                    f"{row['State/UT']}</div>"
                    f"<span style='font-size:0.8rem;font-weight:600;color:{grade_color(row[\"Grade\"])}'>"
                    f"{row['Total']:.1f}</span></div>", unsafe_allow_html=True)

        history = [
            {"Assessment": snap["label"], "Score": snap["scores"].get(sel, {}).get("total", 0)}
            for d_key, snap in sorted(data["assessments"].items()) if sel in snap["scores"]
        ]
        if len(history) > 1:
            st.markdown("<br><div class='section-title'>Score History</div>", unsafe_allow_html=True)
            hist_df = pd.DataFrame(history)
            fig_h = go.Figure(go.Scatter(
                x=hist_df["Assessment"], y=hist_df["Score"],
                mode="lines+markers",
                line=dict(color=grade_color(grade), width=2.5),
                marker=dict(size=10, color=grade_color(grade)),
                fill="tozeroy", fillcolor=grade_color(grade) + "15",
                hovertemplate="%{x}<br>Score: %{y}<extra></extra>",
            ))
            apply_theme(fig_h, height=280, margin=dict(l=50, r=20, t=20, b=60))
            style_axes(fig_h, ytitle="Score")
            fig_h.update_yaxes(range=[0, 105])
            fig_h.update_xaxes(tickangle=-20)
            st.plotly_chart(fig_h, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPARE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare":
    cs1, cs2 = st.columns(2)
    with cs1:
        st.markdown("<div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
                    "letter-spacing:1px;color:#185FA5;margin-bottom:6px'>State / UT A</div>",
                    unsafe_allow_html=True)
        sa_name = st.selectbox("A", all_states, index=0, label_visibility="collapsed")
    with cs2:
        st.markdown("<div style='font-size:0.72rem;font-weight:600;text-transform:uppercase;"
                    "letter-spacing:1px;color:#bf360c;margin-bottom:6px'>State / UT B</div>",
                    unsafe_allow_html=True)
        sb_name = st.selectbox("B", all_states, index=min(5, len(all_states)-1), label_visibility="collapsed")

    if sa_name == sb_name:
        st.warning("Please select two different States/UTs.")
    else:
        sa, sb = scores[sa_name], scores[sb_name]
        def gv_all(s):
            return {p["key"]: gv(s, p["key"]) for p in PARAM_META} | \
                   {"total": s.get("total", 0), "grade": s.get("grade", "E")}
        va, vb = gv_all(sa), gv_all(sb)
        a_wins = va["total"] > vb["total"]

        cc1, cc2 = st.columns(2)
        for col, name, v, color, wins in [
            (cc1, sa_name, va, "#185FA5", a_wins),
            (cc2, sb_name, vb, "#bf360c", not a_wins),
        ]:
            with col:
                g = v["grade"]
                winner_tag = ("<div style='font-size:0.65rem;background:#e8f5e9;color:#1b5e20;"
                              "border:1px solid #a5d6a7;border-radius:10px;padding:2px 10px;"
                              "display:inline-block;margin-bottom:6px'>Winner</div>"
                              if wins else "")
                st.markdown(
                    f"<div class='cmp-card' style='border-color:{color if wins else \"#e2e8f0\"};'>"
                    f"{winner_tag}"
                    f"<div style='font-family:\"Playfair Display\",serif;font-size:1.1rem;"
                    f"font-weight:700;color:#1a1a2e;margin-bottom:8px'>{name}</div>"
                    f"{badge_html(g)}"
                    f"<div class='cmp-score' style='color:{grade_color(g)};margin:10px 0'>"
                    f"{v['total']:.1f}</div>"
                    f"<div style='font-size:0.72rem;color:#94a3b8'>out of 100</div>"
                    f"</div>", unsafe_allow_html=True)

        col_rad, col_tbl = st.columns([3, 2])
        with col_rad:
            st.markdown("<div class='section-title'>Radar Comparison</div>", unsafe_allow_html=True)
            st.plotly_chart(chart_compare_radar(sa_name, va, sb_name, vb), use_container_width=True)
        with col_tbl:
            st.markdown("<div class='section-title'>Head-to-Head</div>", unsafe_allow_html=True)
            rows_cmp = []
            for p in PARAM_META:
                av, bv = va[p["key"]], vb[p["key"]]
                win = sa_name if av > bv else (sb_name if bv > av else "Tied")
                rows_cmp.append({
                    "Parameter": p["label"],
                    sa_name: f"{av}/{p['max']}",
                    sb_name: f"{bv}/{p['max']}",
                    "Better": win,
                })
            rows_cmp.append({
                "Parameter": "TOTAL",
                sa_name: f"{va['total']:.1f}",
                sb_name: f"{vb['total']:.1f}",
                "Better": sa_name if a_wins else sb_name,
            })
            st.dataframe(pd.DataFrame(rows_cmp), use_container_width=True, hide_index=True)

            st.markdown("<div class='section-title' style='margin-top:1rem'>Parameter Bars</div>",
                        unsafe_allow_html=True)
            for p in PARAM_META:
                av = va[p["key"]]; bv = vb[p["key"]]
                pa = av / p["max"] * 100; pb = bv / p["max"] * 100
                st.markdown(
                    f"<div style='margin-bottom:10px'>"
                    f"<div style='font-size:0.73rem;color:#64748b;margin-bottom:3px'>{p['label']}</div>"
                    f"<div style='display:flex;align-items:center;gap:6px'>"
                    f"<span style='min-width:26px;text-align:right;font-size:0.73rem;"
                    f"font-weight:600;color:#185FA5'>{av}</span>"
                    f"<div style='flex:1;height:6px;background:#e2e8f0;border-radius:3px;"
                    f"position:relative;overflow:hidden'>"
                    f"<div style='position:absolute;right:50%;width:{pa/2:.1f}%;height:100%;"
                    f"background:#185FA5;border-radius:3px 0 0 3px;top:0'></div>"
                    f"<div style='position:absolute;left:50%;width:{pb/2:.1f}%;height:100%;"
                    f"background:#bf360c;border-radius:0 3px 3px 0;top:0'></div>"
                    f"</div>"
                    f"<span style='min-width:26px;font-size:0.73rem;font-weight:600;"
                    f"color:#bf360c'>{bv}</span></div></div>",
                    unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  HEATMAP
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🗺️ Heatmap":
    st.markdown("<div class='section-title'>Parameter Achievement — % of Maximum Marks</div>",
                unsafe_allow_html=True)
    st.plotly_chart(chart_heatmap_plotly(df), use_container_width=True)

    param_keys  = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
    param_maxes = [32, 25, 23, 15, 5]
    param_cols  = ["#185FA5", "#1b5e20", "#bf360c", "#BA7517", "#4a148c"]
    legend_html = "<div style='display:flex;flex-wrap:wrap;gap:14px;margin-top:0.5rem'>"
    for lbl, col in zip(param_keys, param_cols):
        legend_html += (f"<span style='display:flex;align-items:center;gap:5px;font-size:0.72rem'>"
                        f"<span style='width:12px;height:12px;border-radius:2px;"
                        f"background:{col}88;display:inline-block'></span>"
                        f"<span style='color:#64748b'>{lbl}</span></span>")
    legend_html += "</div>"
    st.markdown(legend_html, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    if len(data["assessments"]) < 2:
        st.info("Add at least 2 assessments to see trends.")
    else:
        tc1, tc2 = st.columns([3, 1])
        sel_states = tc1.multiselect(
            "Select States/UTs", sorted(BASELINE.keys()),
            default=["Punjab", "Karnataka", "Uttar Pradesh", "Delhi", "Tripura"],
        )
        param_opts = ["Total Score","Res. Adequacy","Fin. Viability",
                      "Ease of Living","Energy Transition","Reg. Governance"]
        param = tc2.selectbox("Parameter", param_opts)

        rows = []
        for d_key, snap in sorted(data["assessments"].items()):
            for stn in sel_states:
                sc = snap["scores"].get(stn, {})
                if sc:
                    rows.append({
                        "Date": d_key, "State/UT": stn,
                        "Total Score":       sc.get("total", 0),
                        "Res. Adequacy":     gv(sc,"ra","resource_adequacy"),
                        "Fin. Viability":    gv(sc,"fv","financial_viability"),
                        "Ease of Living":    gv(sc,"el","ease_of_living"),
                        "Energy Transition": gv(sc,"et","energy_transition"),
                        "Reg. Governance":   gv(sc,"rg","regulatory_governance"),
                    })
        if rows:
            tdf = pd.DataFrame(rows)
            st.plotly_chart(chart_trend(tdf, param), use_container_width=True)

            all_d = sorted(data["assessments"].keys())
            if len(all_d) >= 2:
                chg = []
                for state in sorted(BASELINE.keys()):
                    s1 = data["assessments"][all_d[0]]["scores"].get(state, {})
                    s2 = data["assessments"][all_d[-1]]["scores"].get(state, {})
                    if s1 and s2:
                        delta = round(s2.get("total",0) - s1.get("total",0), 2)
                        chg.append({
                            "State/UT": state,
                            f"Score ({all_d[0]})": s1.get("total", 0),
                            f"Score ({all_d[-1]})": s2.get("total", 0),
                            "Δ": delta,
                            "Direction": "▲ Improved" if delta > 0 else ("▼ Declined" if delta < 0 else "→ Same"),
                        })
                if chg:
                    chg_df = pd.DataFrame(chg).sort_values("Δ", ascending=False)
                    st.plotly_chart(chart_delta(chg_df), use_container_width=True)
                    st.dataframe(chg_df, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  UPLOAD
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload":
    st.markdown(
        "<div class='alert-box'>"
        "Upload a <strong>CSV file</strong> with assessment data. Required columns: "
        "<strong>State/UT</strong>, <strong>Resource Adequacy</strong>, "
        "<strong>Financial Viability</strong>, <strong>Ease of Living</strong>, "
        "<strong>Energy Transition</strong>, <strong>Regulatory Governance</strong>"
        "</div>", unsafe_allow_html=True)

    st.download_button("⬇️ Download CSV Template", make_csv_template(),
                       "assessment_template.csv", mime="text/csv")
    st.markdown("---")

    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        parsed = parse_csv_upload(uploaded)
        if parsed is None:
            st.error("Could not parse file. Check column names match the template.")
        else:
            st.success(f"Parsed {len(parsed)} states/UTs successfully!")
            prev_rows = [
                {"State/UT": st_name, "RA": sc["ra"], "FV": sc["fv"],
                 "EL": sc["el"], "ET": sc["et"], "RG": sc["rg"],
                 "Total": sc["total"], "Grade": sc["grade"]}
                for st_name, sc in parsed.items()
            ]
            prev_df = pd.DataFrame(prev_rows).sort_values("Total", ascending=False)
            st.dataframe(
                prev_df.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100),
                use_container_width=True, height=300)

            uc1, uc2 = st.columns(2)
            up_date  = uc1.date_input("Assessment Date", value=date.today())
            up_label = uc2.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27")
            up_notes = st.text_area("Notes", placeholder="Source, methodology…")

            if st.button("💾 Save Assessment", type="primary", use_container_width=True):
                if not up_label.strip():
                    st.error("Please provide a label.")
                else:
                    dk = str(up_date)
                    data["assessments"][dk] = {
                        "date": dk, "label": up_label,
                        "scores": parsed, "notes": up_notes,
                    }
                    data["audit_log"].append({
                        "action": "file_upload", "date": dk, "label": up_label,
                        "states": len(parsed), "timestamp": datetime.now().isoformat(),
                    })
                    save_data(data)
                    st.success(f"Saved '{up_label}' with {len(parsed)} states!")
                    st.balloons()


# ══════════════════════════════════════════════════════════════════════════════
#  NEW ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed.")
    with st.form("new_assessment_form"):
        nc1, nc2 = st.columns(2)
        adate  = nc1.date_input("Assessment Date", value=date.today(), max_value=date.today())
        alabel = nc2.text_input("Label", placeholder="e.g. ARR FY 2026-27")
        anotes = st.text_area("Notes", placeholder="Key policy changes, data sources…")
        st.markdown("---")

        prev_sc  = snapshot["scores"]
        new_scores = {}

        for state in sorted(BASELINE.keys()):
            p = prev_sc.get(state, {})
            with st.expander(
                f"📍 {state}  ·  Last: {p.get('total',0):.1f}  ·  Grade {p.get('grade','—')}"
            ):
                i1,i2,i3,i4,i5 = st.columns(5)
                n_ra = i1.number_input("RA (0-32)", 0.0, 32.0, float(gv(p,"ra")), 0.5, key=f"{state}_ra")
                n_fv = i2.number_input("FV (0-25)", 0.0, 25.0, float(gv(p,"fv")), 0.5, key=f"{state}_fv")
                n_el = i3.number_input("EL (0-23)", 0.0, 23.0, float(gv(p,"el")), 0.5, key=f"{state}_el")
                n_et = i4.number_input("ET (0-15)", 0.0, 15.0, float(gv(p,"et")), 0.5, key=f"{state}_et")
                n_rg = i5.number_input("RG (0-5)",  0.0,  5.0, float(gv(p,"rg")), 0.5, key=f"{state}_rg")
                n_tot = round(n_ra + n_fv + n_el + n_et + n_rg, 2)
                st.markdown(
                    f"<div style='font-weight:600;font-size:0.85rem;color:{score_to_color(n_tot)}'>"
                    f"→ Total: {n_tot} / 100 — Grade {get_grade(n_tot)}</div>",
                    unsafe_allow_html=True)
                new_scores[state] = {
                    "ra": n_ra, "fv": n_fv, "el": n_el, "et": n_et, "rg": n_rg,
                    "total": n_tot, "grade": get_grade(n_tot),
                }

        if st.form_submit_button("💾 Save Assessment", type="primary", use_container_width=True):
            if not alabel.strip():
                st.error("Please enter a label.")
            else:
                dk = str(adate)
                data["assessments"][dk] = {
                    "date": dk, "label": alabel,
                    "scores": new_scores, "notes": anotes,
                }
                data["audit_log"].append({
                    "action": "new_assessment", "date": dk, "label": alabel,
                    "timestamp": datetime.now().isoformat(),
                })
                save_data(data)
                st.success(f"Saved '{alabel}'!")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 History":
    st.markdown("<div class='section-title'>Assessment History</div>", unsafe_allow_html=True)
    rows_h = []
    for d_key, snap in sorted(data["assessments"].items(), reverse=True):
        sc  = snap["scores"]
        avg = round(sum(v.get("total", 0) for v in sc.values()) / max(len(sc), 1), 2)
        rows_h.append({
            "Date":       d_key,
            "Label":      snap["label"],
            "States":     len(sc),
            "Avg Score":  avg,
            "Notes":      snap.get("notes", "")[:60],
        })
    st.dataframe(pd.DataFrame(rows_h), use_container_width=True, hide_index=True)

    if data["audit_log"]:
        st.markdown("<br><div class='section-title'>Audit Log</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(data["audit_log"]), use_container_width=True, hide_index=True)

    st.markdown("---")
    deletable = [d for d in sorted(data["assessments"].keys()) if d != "2025-03-31"]
    if deletable:
        del_sel = st.selectbox("Delete assessment (baseline protected)", deletable)
        if st.button("🗑️ Delete", type="secondary"):
            del data["assessments"][del_sel]
            save_data(data)
            st.success(f"Deleted {del_sel}")
            st.rerun()
    else:
        st.info("Only the baseline exists. Add new assessments to manage them here.")


# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='font-size:0.72rem;color:#94a3b8;text-align:center;font-family:\"IBM Plex Sans\",sans-serif'>"
    "First Report: Rating Regulatory Performance of States & UTs &nbsp;|&nbsp; "
    "Power Foundation of India &amp; REC Ltd. &nbsp;|&nbsp; Ministry of Power, GoI"
    "</div>",
    unsafe_allow_html=True)
