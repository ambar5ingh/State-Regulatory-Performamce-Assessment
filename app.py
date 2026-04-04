import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import json
import os
from datetime import datetime, date
import io

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Regulatory Performance – States & UTs",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp { background: #f0f2f6; }

.header-box {
    background: linear-gradient(135deg, #0d1b4b 0%, #1a3a7c 50%, #0f5499 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.8rem;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(13,27,75,0.25);
    position: relative;
    overflow: hidden;
}
.header-box::before {
    content: "⚡";
    position: absolute;
    right: 2rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 5rem;
    opacity: 0.08;
}
.header-box h1 {
    margin: 0;
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.5px;
}
.header-box p { margin: 0.4rem 0 0; opacity: 0.75; font-size: 0.82rem; font-weight: 300; }
.header-box .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    margin-top: 0.6rem;
    font-weight: 500;
}

.kpi-card {
    background: white;
    border-radius: 14px;
    padding: 1.3rem 1.4rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8eaed;
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100%;
}
.kpi-card:hover { transform: translateY(-2px); box-shadow: 0 6px 24px rgba(0,0,0,0.10); }
.kpi-val { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; line-height: 1; }
.kpi-lbl { font-size: 0.73rem; color: #888; margin-top: 4px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.5px; }
.kpi-sub { font-size: 0.78rem; color: #555; margin-top: 2px; }

.grade-pill {
    display: inline-block;
    padding: 3px 14px;
    border-radius: 20px;
    font-weight: 700;
    font-size: 0.82rem;
    font-family: 'Syne', sans-serif;
}
.gA { background: #e8f5e9; color: #1b5e20; border: 1px solid #a5d6a7; }
.gB { background: #e3f2fd; color: #0d47a1; border: 1px solid #90caf9; }
.gC { background: #fff3e0; color: #bf360c; border: 1px solid #ffcc80; }
.gD { background: #fce4ec; color: #880e4f; border: 1px solid #f48fb1; }
.gE { background: #f3e5f5; color: #4a148c; border: 1px solid #ce93d8; }

.param-block {
    background: white;
    border-left: 4px solid #1a3a7c;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.4rem;
    margin-bottom: 0.9rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}
.param-block .ptitle { font-weight: 600; color: #0d1b4b; margin-bottom: 8px; font-size: 0.88rem; }

.section-card {
    background: white;
    border-radius: 14px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border: 1px solid #e8eaed;
    margin-bottom: 1rem;
}

.state-scorecard {
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border: 1px solid #e8eaed;
}

.upload-zone {
    background: linear-gradient(135deg, #f0f4ff, #e8f0fe);
    border: 2px dashed #7986cb;
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    margin-bottom: 1rem;
}

.info-banner {
    background: linear-gradient(90deg, #e8f5e9, #f1f8e9);
    border-left: 4px solid #43a047;
    border-radius: 0 10px 10px 0;
    padding: 0.8rem 1.2rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    color: #2e7d32;
}

.stTabs [data-baseweb="tab-list"] {
    background: #f8f9fa;
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    font-weight: 500;
    font-size: 0.85rem;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1b4b 0%, #1a3a7c 100%);
}
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] .stRadio label { 
    background: rgba(255,255,255,0.08) !important;
    border-radius: 8px !important;
    padding: 0.6rem 1rem !important;
    margin: 2px 0 !important;
    border: 1px solid rgba(255,255,255,0.05) !important;
    font-size: 0.85rem !important;
    cursor: pointer;
    transition: background 0.2s;
}
[data-testid="stSidebar"] .stRadio label:hover { background: rgba(255,255,255,0.15) !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"
GRADE_COLOR = {"A":"#1b5e20","B":"#0d47a1","C":"#bf360c","D":"#880e4f","E":"#4a148c"}
GRADE_BG    = {"A":"#e8f5e9","B":"#e3f2fd","C":"#fff3e0","D":"#fce4ec","E":"#f3e5f5"}
GRADE_CSS   = {"A":"gA","B":"gB","C":"gC","D":"gD","E":"gE"}
PARAMS = [
    ("Resource Adequacy",    "ra", 32),
    ("Financial Viability",  "fv", 25),
    ("Ease of Living",       "el", 23),
    ("Energy Transition",    "et", 15),
    ("Regulatory Governance","rg", 5),
]

BASELINE = {
    "Punjab":               {"ra":32,"fv":25,"el":23,"et":12,"rg":5,  "total":97.0,  "grade":"A","region":"North",     "type":"State"},
    "Karnataka":            {"ra":32,"fv":23,"el":22,"et":14,"rg":5,  "total":96.0,  "grade":"A","region":"South",     "type":"State"},
    "Maharashtra":          {"ra":30,"fv":22,"el":23,"et":14,"rg":5,  "total":94.0,  "grade":"A","region":"West",      "type":"State"},
    "Assam":                {"ra":32,"fv":24,"el":20,"et":12,"rg":5,  "total":93.0,  "grade":"A","region":"North-East","type":"State"},
    "Arunachal Pradesh":    {"ra":32,"fv":25,"el":21,"et":8, "rg":5,  "total":91.0,  "grade":"A","region":"North-East","type":"State"},
    "Madhya Pradesh":       {"ra":27,"fv":22,"el":21,"et":14,"rg":5,  "total":89.0,  "grade":"A","region":"Central",   "type":"State"},
    "Meghalaya":            {"ra":32,"fv":19,"el":20,"et":13,"rg":5,  "total":89.0,  "grade":"A","region":"North-East","type":"State"},
    "Haryana":              {"ra":28,"fv":21,"el":20,"et":15,"rg":4.5,"total":88.5,  "grade":"A","region":"North",     "type":"State"},
    "Himachal Pradesh":     {"ra":29,"fv":20,"el":22,"et":12,"rg":5,  "total":88.0,  "grade":"A","region":"North",     "type":"State"},
    "Mizoram":              {"ra":32,"fv":18,"el":20,"et":12,"rg":5,  "total":87.0,  "grade":"A","region":"North-East","type":"State"},
    "Jharkhand":            {"ra":28,"fv":22,"el":19,"et":13,"rg":4.67,"total":86.67,"grade":"A","region":"East",      "type":"State"},
    "Sikkim":               {"ra":24,"fv":20,"el":18,"et":11,"rg":5,  "total":78.0,  "grade":"B","region":"North-East","type":"State"},
    "Odisha":               {"ra":24,"fv":18,"el":17,"et":12,"rg":4.5,"total":75.5,  "grade":"B","region":"East",      "type":"State"},
    "Chandigarh":           {"ra":22,"fv":18,"el":19,"et":10,"rg":5,  "total":74.0,  "grade":"B","region":"North",     "type":"UT"},
    "Dadra & NH and DD":    {"ra":22,"fv":17,"el":19,"et":11,"rg":5,  "total":74.0,  "grade":"B","region":"West",      "type":"UT"},
    "Andaman & Nicobar":    {"ra":28,"fv":9, "el":16,"et":14,"rg":5,  "total":72.0,  "grade":"B","region":"Island UT", "type":"UT"},
    "Lakshadweep":          {"ra":26,"fv":14,"el":17,"et":10,"rg":5,  "total":72.0,  "grade":"B","region":"Island UT", "type":"UT"},
    "Gujarat":              {"ra":18,"fv":19,"el":18,"et":11,"rg":5,  "total":71.0,  "grade":"B","region":"West",      "type":"State"},
    "Goa":                  {"ra":20,"fv":17,"el":19,"et":10,"rg":5,  "total":71.0,  "grade":"B","region":"West",      "type":"State"},
    "Puducherry":           {"ra":20,"fv":17,"el":18,"et":10,"rg":5,  "total":70.0,  "grade":"B","region":"South",     "type":"UT"},
    "Uttarakhand":          {"ra":20,"fv":16,"el":17,"et":10,"rg":5,  "total":68.0,  "grade":"B","region":"North",     "type":"State"},
    "Andhra Pradesh":       {"ra":10,"fv":20,"el":13,"et":15,"rg":5,  "total":63.0,  "grade":"C","region":"South",     "type":"State"},
    "Ladakh":               {"ra":22,"fv":14,"el":15,"et":7, "rg":5,  "total":63.0,  "grade":"C","region":"North",     "type":"UT"},
    "Manipur":              {"ra":20,"fv":15,"el":14,"et":8, "rg":5,  "total":62.0,  "grade":"C","region":"North-East","type":"State"},
    "Bihar":                {"ra":18,"fv":15,"el":14,"et":9, "rg":5,  "total":61.0,  "grade":"C","region":"East",      "type":"State"},
    "Tamil Nadu":           {"ra":14,"fv":15,"el":16,"et":8, "rg":5,  "total":58.0,  "grade":"C","region":"South",     "type":"State"},
    "Kerala":               {"ra":14,"fv":14,"el":15,"et":8, "rg":4.5,"total":55.5,  "grade":"C","region":"South",     "type":"State"},
    "Nagaland":             {"ra":18,"fv":13,"el":13,"et":6, "rg":5,  "total":55.0,  "grade":"C","region":"North-East","type":"State"},
    "Chhattisgarh":         {"ra":10,"fv":14,"el":14,"et":9, "rg":5,  "total":52.0,  "grade":"C","region":"Central",   "type":"State"},
    "Telangana":            {"ra":12,"fv":13,"el":13,"et":8, "rg":4.5,"total":50.5,  "grade":"C","region":"South",     "type":"State"},
    "West Bengal":          {"ra":14,"fv":12,"el":12,"et":7, "rg":5,  "total":50.0,  "grade":"C","region":"East",      "type":"State"},
    "Jammu & Kashmir":      {"ra":14,"fv":12,"el":13,"et":7, "rg":3,  "total":49.0,  "grade":"D","region":"North",     "type":"UT"},
    "Uttar Pradesh":        {"ra":10,"fv":14,"el":13,"et":8, "rg":3,  "total":48.0,  "grade":"D","region":"North",     "type":"State"},
    "Delhi":                {"ra":8, "fv":10,"el":12,"et":7, "rg":3.5,"total":40.5,  "grade":"D","region":"North",     "type":"UT"},
    "Rajasthan":            {"ra":8, "fv":11,"el":11,"et":6, "rg":3,  "total":39.0,  "grade":"D","region":"North",     "type":"State"},
    "Tripura":              {"ra":5, "fv":6, "el":6, "et":3, "rg":1.5,"total":21.5,  "grade":"E","region":"North-East","type":"State"},
}

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def get_grade(score):
    if score >= 85: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "E"

def grade_pill(g):
    return f'<span class="grade-pill {GRADE_CSS[g]}">Grade {g}</span>'

def score_color(pct):
    if pct >= 85: return GRADE_COLOR["A"]
    if pct >= 65: return GRADE_COLOR["B"]
    if pct >= 50: return GRADE_COLOR["C"]
    if pct >= 35: return GRADE_COLOR["D"]
    return GRADE_COLOR["E"]

def gv(s, *keys):
    for k in keys:
        if k in s: return s[k]
    return 0

# ─── PERSISTENCE ──────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    scores = {st: {"ra":b["ra"],"fv":b["fv"],"el":b["el"],"et":b["et"],"rg":b["rg"],
                   "total":b["total"],"grade":b["grade"]} for st, b in BASELINE.items()}
    data = {"assessments": {"2025-03-31": {
        "date":"2025-03-31","label":"Baseline – Report FY 2024-25",
        "scores":scores,"notes":"First Report: Rating Regulatory Performance of States & UTs (PFI & REC Ltd.)"
    }}, "audit_log": []}
    save_data(data)
    return data

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def build_df(scores):
    rows = []
    for state, s in scores.items():
        b = BASELINE.get(state, {})
        rows.append({
            "State/UT": state, "Region": b.get("region","—"), "Type": b.get("type","—"),
            "Res. Adequacy":     gv(s,"ra","resource_adequacy"),
            "Fin. Viability":    gv(s,"fv","financial_viability"),
            "Ease of Living":    gv(s,"el","ease_of_living"),
            "Energy Transition": gv(s,"et","energy_transition"),
            "Reg. Governance":   gv(s,"rg","regulatory_governance"),
            "Total": s.get("total", 0), "Grade": s.get("grade","E"),
        })
    df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# ─── EXCEL PARSER ─────────────────────────────────────────────────────────────
def parse_excel(file) -> dict | None:
    """
    Expected columns: State/UT | Resource Adequacy | Financial Viability |
                      Ease of Living | Energy Transition | Regulatory Governance
    Returns dict of {state: {ra,fv,el,et,rg,total,grade}} or None on failure.
    """
    try:
        xdf = pd.read_excel(file)
        xdf.columns = xdf.columns.str.strip()
        col_map = {
            "Resource Adequacy":    "ra",
            "Financial Viability":  "fv",
            "Ease of Living":       "el",
            "Energy Transition":    "et",
            "Regulatory Governance":"rg",
        }
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
        st.error(f"Excel parsing error: {e}")
        return None

def make_excel_template():
    rows = []
    for state, b in BASELINE.items():
        rows.append({
            "State/UT": state,
            "Resource Adequacy":    b["ra"],
            "Financial Viability":  b["fv"],
            "Ease of Living":       b["el"],
            "Energy Transition":    b["et"],
            "Regulatory Governance":b["rg"],
        })
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False)
    buf.seek(0)
    return buf

# ─── PLOTLY HELPERS ──────────────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    font_family="DM Sans",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=10, r=10, t=40, b=10),
)

def plotly_bar_rankings(df_sorted):
    colors = [GRADE_COLOR[g] for g in df_sorted["Grade"]]
    fig = go.Figure(go.Bar(
        x=df_sorted["Total"],
        y=df_sorted["State/UT"],
        orientation="h",
        marker_color=colors,
        text=df_sorted["Total"].apply(lambda x: f"{x:.1f}"),
        textposition="outside",
        customdata=df_sorted[["Grade","Region","Type"]].values,
        hovertemplate="<b>%{y}</b><br>Score: %{x}<br>Grade: %{customdata[0]}<br>Region: %{customdata[1]}<br>Type: %{customdata[2]}<extra></extra>",
    ))
    fig.add_vline(x=85, line_dash="dot", line_color="#1b5e20", annotation_text="A", annotation_font_color="#1b5e20")
    fig.add_vline(x=65, line_dash="dot", line_color="#0d47a1", annotation_text="B", annotation_font_color="#0d47a1")
    fig.add_vline(x=50, line_dash="dot", line_color="#bf360c", annotation_text="C", annotation_font_color="#bf360c")
    fig.add_vline(x=35, line_dash="dot", line_color="#880e4f", annotation_text="D", annotation_font_color="#880e4f")
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(500, len(df_sorted)*22),
        xaxis=dict(range=[0,105], showgrid=True, gridcolor="#f0f0f0", title="Score (out of 100)"),
        yaxis=dict(autorange="reversed", tickfont_size=11),
        title="All States & UTs — Performance Ranking",
        showlegend=False,
    )
    return fig

def plotly_grade_donut(gc):
    labels = [f"Grade {g}" for g in gc.index]
    colors = [GRADE_BG[g] for g in gc.index]
    border = [GRADE_COLOR[g] for g in gc.index]
    fig = go.Figure(go.Pie(
        labels=labels, values=gc.values,
        hole=0.55,
        marker=dict(colors=colors, line=dict(color=border, width=2)),
        textinfo="label+value",
        hovertemplate="%{label}: %{value} states<extra></extra>",
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=320, title="Grade Distribution", showlegend=False)
    return fig

def plotly_region_bar(df):
    rdf = df.groupby("Region")["Total"].mean().reset_index().sort_values("Total", ascending=False)
    rdf["color"] = rdf["Total"].apply(score_color)
    fig = px.bar(rdf, x="Region", y="Total", color="Total",
                 color_continuous_scale=["#fce4ec","#fff3e0","#e3f2fd","#e8f5e9"],
                 text=rdf["Total"].apply(lambda x: f"{x:.1f}"),
                 title="Average Score by Region")
    fig.update_traces(textposition="outside")
    fig.update_layout(**PLOTLY_LAYOUT, height=320, coloraxis_showscale=False,
                      yaxis=dict(range=[0,105], showgrid=True, gridcolor="#f0f0f0"))
    return fig

def plotly_heatmap(df):
    heat = df.set_index("State/UT")[["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]].copy()
    maxes = [32,25,23,15,5]
    for col, mx in zip(heat.columns, maxes):
        heat[col] = (heat[col]/mx*100).round(1)
    fig = go.Figure(go.Heatmap(
        z=heat.values,
        x=heat.columns.tolist(),
        y=heat.index.tolist(),
        colorscale="RdYlGn",
        zmin=0, zmax=100,
        text=heat.values,
        texttemplate="%{text:.0f}%",
        textfont_size=9,
        hovertemplate="<b>%{y}</b><br>%{x}: %{z:.1f}%<extra></extra>",
        colorbar=dict(title="% of Max", ticksuffix="%"),
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=max(600, len(heat)*20),
        title="Parameter Achievement Heatmap (% of Max Marks)",
        xaxis=dict(side="top"),
        yaxis=dict(autorange="reversed", tickfont_size=10),
    )
    return fig

def plotly_radar(state_name, vals, maxes):
    pcts = [v/m*100 for v,m in zip(vals, maxes)]
    cats = ["Resource\nAdequacy","Financial\nViability","Ease of\nLiving","Energy\nTransition","Regulatory\nGovernance"]
    fig = go.Figure(go.Scatterpolar(
        r=pcts + [pcts[0]],
        theta=cats + [cats[0]],
        fill="toself",
        fillcolor=f"rgba(26,58,124,0.15)",
        line=dict(color="#1a3a7c", width=2),
        name=state_name,
        hovertemplate="%{theta}: %{r:.1f}%<extra></extra>",
    ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(
            radialaxis=dict(visible=True, range=[0,100], ticksuffix="%", gridcolor="#e0e0e0"),
            angularaxis=dict(gridcolor="#e0e0e0"),
        ),
        height=350,
        title=f"Parameter Profile – {state_name}",
        showlegend=False,
    )
    return fig

def plotly_compare_radar(sa_name, va, sb_name, vb):
    params = ["Resource Adequacy","Financial Viability","Ease of Living","Energy Transition","Regulatory Governance"]
    keys   = ["ra","fv","el","et","rg"]
    maxes  = [32,25,23,15,5]
    cats   = ["Resource\nAdequacy","Financial\nViability","Ease of\nLiving","Energy\nTransition","Regulatory\nGovernance"]
    def pcts(v): return [v[k]/m*100 for k,m in zip(keys,maxes)]
    pa, pb = pcts(va), pcts(vb)
    fig = go.Figure()
    for name, p, color in [(sa_name, pa, "#1a3a7c"), (sb_name, pb, "#c62828")]:
        fig.add_trace(go.Scatterpolar(
            r=p+[p[0]], theta=cats+[cats[0]],
            fill="toself",
            fillcolor=f"rgba{tuple(int(color.lstrip('#')[i:i+2],16) for i in (0,2,4))+(0.12,)}",
            line=dict(color=color, width=2),
            name=name,
            hovertemplate=f"<b>{name}</b><br>%{{theta}}: %{{r:.1f}}%<extra></extra>",
        ))
    fig.update_layout(
        **PLOTLY_LAYOUT,
        polar=dict(radialaxis=dict(visible=True, range=[0,100], ticksuffix="%", gridcolor="#e0e0e0"),
                   angularaxis=dict(gridcolor="#e0e0e0")),
        height=400, title="Parameter Comparison",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
    )
    return fig

def plotly_score_gauge(total, grade):
    color = GRADE_COLOR[grade]
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=total,
        domain={"x":[0,1],"y":[0,1]},
        number={"suffix":" / 100","font":{"size":28,"family":"Syne","color":color}},
        gauge={
            "axis":{"range":[0,100],"tickwidth":1,"tickcolor":"#888"},
            "bar":{"color":color, "thickness":0.25},
            "bgcolor":"white",
            "steps":[
                {"range":[0,35],"color":GRADE_BG["E"]},
                {"range":[35,50],"color":GRADE_BG["D"]},
                {"range":[50,65],"color":GRADE_BG["C"]},
                {"range":[65,85],"color":GRADE_BG["B"]},
                {"range":[85,100],"color":GRADE_BG["A"]},
            ],
            "threshold":{"line":{"color":color,"width":3},"thickness":0.8,"value":total},
        }
    ))
    fig.update_layout(**PLOTLY_LAYOUT, height=250, margin=dict(l=20,r=20,t=20,b=20))
    return fig

def plotly_scatter_bubble(df):
    fig = px.scatter(
        df, x="Fin. Viability", y="Res. Adequacy",
        size="Total", color="Grade",
        hover_name="State/UT",
        color_discrete_map=GRADE_COLOR,
        text="State/UT",
        title="Resource Adequacy vs Financial Viability (bubble = total score)",
        labels={"Fin. Viability":"Financial Viability (out of 25)",
                "Res. Adequacy":"Resource Adequacy (out of 32)"},
        size_max=40,
    )
    fig.update_traces(textposition="top center", textfont_size=8)
    fig.update_layout(**PLOTLY_LAYOUT, height=480,
                      xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                      yaxis=dict(showgrid=True, gridcolor="#f0f0f0"))
    return fig

def plotly_treemap(df):
    fig = px.treemap(
        df, path=["Region","State/UT"], values="Total",
        color="Total",
        color_continuous_scale=["#fce4ec","#fff3e0","#e3f2fd","#e8f5e9"],
        hover_data={"Grade": True},
        title="Score Distribution by Region (Treemap)",
    )
    fig.update_layout(**PLOTLY_LAYOUT, height=450, coloraxis_showscale=True,
                      coloraxis_colorbar=dict(title="Score"))
    fig.update_traces(textinfo="label+value")
    return fig

def plotly_type_comparison(df):
    fig = px.box(df, x="Type", y="Total", color="Type",
                 color_discrete_map={"State":"#1a3a7c","UT":"#c62828"},
                 title="Score Distribution: States vs Union Territories",
                 points="all", hover_name="State/UT")
    fig.update_layout(**PLOTLY_LAYOUT, height=380,
                      yaxis=dict(title="Total Score", showgrid=True, gridcolor="#f0f0f0"),
                      showlegend=False)
    return fig

def plotly_param_distribution(df):
    params = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]
    fig = go.Figure()
    colors = ["#1a3a7c","#0288d1","#26a69a","#43a047","#f57c00"]
    for p, c in zip(params, colors):
        fig.add_trace(go.Violin(y=df[p], name=p, fillcolor=c, line_color=c, opacity=0.6,
                                box_visible=True, meanline_visible=True,
                                hovertemplate=f"<b>{p}</b><br>Value: %{{y}}<extra></extra>"))
    fig.update_layout(**PLOTLY_LAYOUT, height=380,
                      title="Parameter Score Distribution (Violin)",
                      yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                      showlegend=False)
    return fig

# ─── LOAD ─────────────────────────────────────────────────────────────────────
data     = load_data()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-size:2.5rem">⚡</div>
      <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700;letter-spacing:-0.5px">
        Regulatory Performance
      </div>
      <div style="font-size:0.72rem;opacity:0.6;margin-top:2px">States & Union Territories</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Dashboard",
        "🔍 State Profile",
        "📈 Trends",
        "⚖️ Compare",
        "📤 Upload Excel",
        "📝 New Assessment",
        "📋 History",
    ], label_visibility="collapsed")
    st.markdown("---")
    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox("📅 Assessment Period", dates,
                            format_func=lambda d: data["assessments"][d]["label"],
                            label_visibility="visible")
    st.markdown("---")
    st.markdown('<div style="font-size:0.7rem;opacity:0.5;text-align:center">PFI & REC Ltd. | MoP, GoI</div>', unsafe_allow_html=True)

snapshot = data["assessments"][sel_date]
scores   = snapshot["scores"]
df       = build_df(scores)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <h1>⚡ Regulatory Performance Rating — States &amp; UTs</h1>
  <p>Power Foundation of India &amp; REC Ltd. | Ministry of Power, Government of India</p>
  <span class="badge">Resource Adequacy</span>
  <span class="badge">Financial Viability</span>
  <span class="badge">Ease of Living</span>
  <span class="badge">Energy Transition</span>
  <span class="badge">Regulatory Governance</span>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    gc  = df["Grade"].value_counts()
    avg = df["Total"].mean()
    top = df.iloc[0]

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpis = [
        (len(df), "#0d1b4b", "States & UTs", ""),
        (gc.get("A",0), GRADE_COLOR["A"], "Grade A", "≥ 85 marks"),
        (gc.get("B",0), GRADE_COLOR["B"], "Grade B", "65–84 marks"),
        (gc.get("C",0), GRADE_COLOR["C"], "Grade C", "50–64 marks"),
        (gc.get("D",0)+gc.get("E",0), GRADE_COLOR["D"], "Grade D/E", "< 50 marks"),
        (f"{avg:.1f}", "#555", "National Avg", "out of 100"),
    ]
    for col, (val, color, lbl, sub) in zip([c1,c2,c3,c4,c5,c6], kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card">
              <div class="kpi-val" style="color:{color}">{val}</div>
              <div class="kpi-lbl">{lbl}</div>
              {'<div class="kpi-sub">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Rankings", "📊 Charts", "🔬 Deep Dive", "🗺️ Heatmap", "📋 Table"])

    with tab1:
        col_f1, col_f2 = st.columns([3,1])
        with col_f1:
            search = st.text_input("🔍 Search state/UT", placeholder="Type to filter...", label_visibility="collapsed")
        with col_f2:
            filter_type = st.selectbox("Type", ["All","State","UT"], label_visibility="collapsed")
        
        fdf = df.copy()
        if search:
            fdf = fdf[fdf["State/UT"].str.contains(search, case=False)]
        if filter_type != "All":
            fdf = fdf[fdf["Type"] == filter_type]
        
        st.plotly_chart(plotly_bar_rankings(fdf.sort_values("Total", ascending=True)), use_container_width=True)

    with tab2:
        r1c1, r1c2 = st.columns(2)
        with r1c1:
            st.plotly_chart(plotly_grade_donut(gc), use_container_width=True)
        with r1c2:
            st.plotly_chart(plotly_region_bar(df), use_container_width=True)
        
        r2c1, r2c2 = st.columns(2)
        with r2c1:
            st.plotly_chart(plotly_type_comparison(df), use_container_width=True)
        with r2c2:
            st.plotly_chart(plotly_param_distribution(df), use_container_width=True)

    with tab3:
        st.plotly_chart(plotly_scatter_bubble(df), use_container_width=True)
        st.plotly_chart(plotly_treemap(df), use_container_width=True)

    with tab4:
        st.plotly_chart(plotly_heatmap(df), use_container_width=True)

    with tab5:
        disp = df.copy()
        disp.insert(0, "Rank", disp.index)
        st.dataframe(
            disp.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100),
            use_container_width=True, height=600
        )
        buf = io.BytesIO()
        disp.to_excel(buf, index=False)
        buf.seek(0)
        st.download_button("⬇️ Download as Excel", buf, "regulatory_rankings.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ══════════════════════════════════════════════════════════════════════════════
# STATE PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 State Profile":
    c1, c2 = st.columns([2,1])
    with c1:
        sel = st.selectbox("Select State / UT", sorted(scores.keys()))
    with c2:
        show_peers = st.checkbox("Show regional peers", value=False)

    s     = scores[sel]
    b     = BASELINE.get(sel, {})
    ra    = gv(s,"ra","resource_adequacy")
    fv    = gv(s,"fv","financial_viability")
    el    = gv(s,"el","ease_of_living")
    et    = gv(s,"et","energy_transition")
    rg    = gv(s,"rg","regulatory_governance")
    total = s.get("total", 0)
    grade = s.get("grade", get_grade(total))
    gc_color = GRADE_COLOR[grade]
    rank_list = df[df["State/UT"]==sel].index.tolist()
    rank_str  = str(rank_list[0]) if rank_list else "—"

    col1, col2, col3 = st.columns([1,1,2])
    with col1:
        st.markdown(f"""
        <div class="state-scorecard">
          <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#0d1b4b">{sel}</div>
          <div style="margin:8px 0">{grade_pill(grade)}</div>
          <div style="font-size:0.8rem;color:#888;margin-bottom:8px">Rank <b>{rank_str}</b> of {len(df)}</div>
          <div style="font-size:0.78rem;color:#666">
            🗺️ {b.get('region','—')} &nbsp;|&nbsp; 🏛️ {b.get('type','—')}
          </div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.plotly_chart(plotly_score_gauge(total, grade), use_container_width=True)
    with col3:
        vals  = [ra, fv, el, et, rg]
        maxes = [32, 25, 23, 15,  5]
        st.plotly_chart(plotly_radar(sel, vals, maxes), use_container_width=True)

    st.markdown("#### Parameter Breakdown")
    p1, p2 = st.columns(2)
    for i, (label, val, mx) in enumerate([("Resource Adequacy",ra,32),("Financial Viability",fv,25),
                                           ("Ease of Living",el,23),("Energy Transition",et,15),
                                           ("Regulatory Governance",rg,5)]):
        pct = val/mx*100
        col = score_color(pct)
        target = p1 if i % 2 == 0 else p2
        with target:
            st.markdown(f"""
            <div class="param-block">
              <div class="ptitle">{label}
                <span style="float:right;color:{col};font-weight:700">{val} / {mx} &nbsp; ({pct:.0f}%)</span>
              </div>
              <div style="background:#e8eaed;border-radius:6px;height:10px">
                <div style="width:{int(pct)}%;background:{col};height:10px;border-radius:6px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    # Regional peers
    if show_peers:
        region = b.get("region","")
        peers  = df[df["Region"]==region].sort_values("Total", ascending=False)
        st.markdown(f"#### 🌏 Regional Peers — {region}")
        fig = px.bar(peers, x="State/UT", y="Total", color="Grade",
                     color_discrete_map=GRADE_COLOR,
                     text="Total", title=f"{region} Region Rankings")
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig.update_layout(**PLOTLY_LAYOUT, height=320,
                          yaxis=dict(range=[0,110], showgrid=True, gridcolor="#f0f0f0"))
        st.plotly_chart(fig, use_container_width=True)

    history = [{"Assessment": snap["label"], "Score": snap["scores"].get(sel,{}).get("total",0)}
               for d, snap in sorted(data["assessments"].items())
               if sel in snap["scores"]]
    if len(history) > 1:
        st.markdown("---")
        hist_df = pd.DataFrame(history)
        fig = px.line(hist_df, x="Assessment", y="Score", markers=True,
                      title=f"📈 Score History — {sel}",
                      color_discrete_sequence=["#1a3a7c"])
        fig.update_traces(line_width=3, marker_size=10)
        fig.update_layout(**PLOTLY_LAYOUT, height=300,
                          yaxis=dict(range=[0,105], showgrid=True, gridcolor="#f0f0f0"))
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    if len(data["assessments"]) < 2:
        st.info("ℹ️ Add at least 2 assessments (via 'New Assessment' or 'Upload Excel') to see trends.")
    else:
        c1, c2 = st.columns([3,1])
        with c1:
            sel_states = st.multiselect("Select States/UTs", sorted(BASELINE.keys()),
                                        default=["Punjab","Karnataka","Uttar Pradesh","Delhi","Tripura"])
        with c2:
            param = st.selectbox("Parameter", ["Total Score","Res. Adequacy","Fin. Viability",
                                               "Ease of Living","Energy Transition","Reg. Governance"])
        rows = []
        for d, snap in sorted(data["assessments"].items()):
            for stn in sel_states:
                sc = snap["scores"].get(stn, {})
                if sc:
                    rows.append({"Date":d,"State/UT":stn,
                                 "Total Score": sc.get("total",0),
                                 "Res. Adequacy":    gv(sc,"ra","resource_adequacy"),
                                 "Fin. Viability":   gv(sc,"fv","financial_viability"),
                                 "Ease of Living":   gv(sc,"el","ease_of_living"),
                                 "Energy Transition":gv(sc,"et","energy_transition"),
                                 "Reg. Governance":  gv(sc,"rg","regulatory_governance")})
        if rows:
            tdf = pd.DataFrame(rows)
            fig = px.line(tdf, x="Date", y=param, color="State/UT",
                          markers=True, title=f"Trend: {param}",
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_traces(line_width=2.5, marker_size=8)
            fig.update_layout(**PLOTLY_LAYOUT, height=400,
                              yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                              legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
            st.plotly_chart(fig, use_container_width=True)

            all_d = sorted(data["assessments"].keys())
            if len(all_d) >= 2:
                st.markdown("#### Change: First vs Latest")
                chg = []
                for state in sorted(BASELINE.keys()):
                    s1 = data["assessments"][all_d[0]]["scores"].get(state,{})
                    s2 = data["assessments"][all_d[-1]]["scores"].get(state,{})
                    if s1 and s2:
                        delta = round(s2.get("total",0)-s1.get("total",0), 2)
                        chg.append({"State/UT":state,
                                    f"Score ({all_d[0]})":s1.get("total",0),
                                    f"Score ({all_d[-1]})":s2.get("total",0),
                                    "Δ":delta,
                                    "Direction":"▲ Improved" if delta>0 else ("▼ Declined" if delta<0 else "→ Same")})
                chg_df = pd.DataFrame(chg).sort_values("Δ", ascending=False)
                fig2 = px.bar(chg_df, x="State/UT", y="Δ", color="Δ",
                              color_continuous_scale=["#c62828","#ffcdd2","#e8f5e9","#1b5e20"],
                              title="Score Change: First → Latest Assessment",
                              text="Δ")
                fig2.update_traces(texttemplate="%{text:+.1f}", textposition="outside")
                fig2.update_layout(**PLOTLY_LAYOUT, height=380,
                                   yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
                                   coloraxis_showscale=False,
                                   xaxis=dict(tickangle=-45))
                st.plotly_chart(fig2, use_container_width=True)
                st.dataframe(chg_df, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# COMPARE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "⚖️ Compare":
    state_list = sorted(scores.keys())
    c1, c2 = st.columns(2)
    sa_name = c1.selectbox("🔵 State/UT A", state_list, index=0)
    sb_name = c2.selectbox("🔴 State/UT B", state_list, index=1)

    if sa_name == sb_name:
        st.warning("Please select two different States/UTs.")
    else:
        sa, sb = scores[sa_name], scores[sb_name]
        def gv_all(s):
            return {"ra":gv(s,"ra","resource_adequacy"),"fv":gv(s,"fv","financial_viability"),
                    "el":gv(s,"el","ease_of_living"),"et":gv(s,"et","energy_transition"),
                    "rg":gv(s,"rg","regulatory_governance"),"total":s.get("total",0),"grade":s.get("grade","E")}
        va, vb = gv_all(sa), gv_all(sb)

        # Score cards
        cc1, cc2 = st.columns(2)
        for col, name, v in [(cc1,sa_name,va),(cc2,sb_name,vb)]:
            with col:
                g = v["grade"]
                winner = "🏆 " if v["total"] > (vb["total"] if name==sa_name else va["total"]) else ""
                st.markdown(f"""
                <div class="state-scorecard">
                  <div style="font-size:1.1rem;font-family:'Syne',sans-serif;font-weight:800;color:#0d1b4b">
                    {winner}{name}
                  </div>
                  <div style="margin:8px 0">{grade_pill(g)}</div>
                  <div style="font-size:3rem;font-weight:800;color:{GRADE_COLOR[g]};font-family:'Syne',sans-serif">
                    {v['total']}
                  </div>
                  <div style="color:#888;font-size:0.78rem">out of 100</div>
                </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        r1, r2 = st.columns([3,2])
        with r1:
            st.plotly_chart(plotly_compare_radar(sa_name, va, sb_name, vb), use_container_width=True)
        with r2:
            cmp_rows = []
            params_list = [("Resource Adequacy","ra",32),("Financial Viability","fv",25),
                           ("Ease of Living","el",23),("Energy Transition","et",15),
                           ("Regulatory Governance","rg",5),("TOTAL","total",100)]
            for label, key, mx in params_list:
                av, bv = va[key], vb[key]
                win = f"✅ {sa_name}" if av>bv else (f"✅ {sb_name}" if bv>av else "Tied")
                cmp_rows.append({"Parameter":label, sa_name:f"{av}/{mx}", sb_name:f"{bv}/{mx}", "Better":win})
            st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)

        # grouped bar
        params_short = ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Trans.","Reg. Governance"]
        maxes = [32,25,23,15,5]
        keys  = ["ra","fv","el","et","rg"]
        fig = go.Figure()
        for name, v, color in [(sa_name,va,"#1a3a7c"),(sb_name,vb,"#c62828")]:
            fig.add_trace(go.Bar(
                name=name,
                x=params_short,
                y=[v[k]/m*100 for k,m in zip(keys,maxes)],
                marker_color=color,
                text=[f"{v[k]/m*100:.0f}%" for k,m in zip(keys,maxes)],
                textposition="outside",
                hovertemplate=f"<b>{name}</b><br>%{{x}}: %{{y:.1f}}%<extra></extra>",
            ))
        fig.update_layout(
            **PLOTLY_LAYOUT, height=380, barmode="group",
            title="Parameter Comparison (% of Max)",
            yaxis=dict(range=[0,115], title="% of Max", showgrid=True, gridcolor="#f0f0f0"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD EXCEL
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload Excel":
    st.markdown("""
    <div class="info-banner">
      ✅ Upload an Excel file with assessment data to create a new assessment period instantly.
      The file must contain: <b>State/UT</b> column + parameter columns.
    </div>""", unsafe_allow_html=True)

    # Download template
    col_dl, col_fmt = st.columns([1,2])
    with col_dl:
        buf = make_excel_template()
        st.download_button("⬇️ Download Excel Template", buf, "assessment_template.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           use_container_width=True)
    with col_fmt:
        st.markdown("""
        **Expected columns:**
        `State/UT` | `Resource Adequacy` | `Financial Viability` | `Ease of Living` | `Energy Transition` | `Regulatory Governance`
        """)

    st.markdown("---")
    uploaded = st.file_uploader("📂 Upload Assessment Excel File", type=["xlsx","xls"],
                                label_visibility="visible")
    if uploaded:
        parsed = parse_excel(uploaded)
        if parsed is None:
            st.error("❌ Could not parse the file. Ensure it has the correct columns.")
        else:
            st.success(f"✅ Parsed {len(parsed)} states/UTs successfully!")
            # Preview
            prev_rows = []
            for state, sc in parsed.items():
                prev_rows.append({"State/UT":state,"RA":sc["ra"],"FV":sc["fv"],
                                  "EL":sc["el"],"ET":sc["et"],"RG":sc["rg"],
                                  "Total":sc["total"],"Grade":sc["grade"]})
            prev_df = pd.DataFrame(prev_rows).sort_values("Total", ascending=False)
            st.dataframe(prev_df.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100),
                         use_container_width=True, height=350)

            st.markdown("#### Save as New Assessment")
            c1, c2 = st.columns(2)
            up_date  = c1.date_input("Assessment Date", value=date.today())
            up_label = c2.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27")
            up_notes = st.text_area("Notes", placeholder="Source, methodology notes...")

            if st.button("💾 Save Excel Assessment", type="primary", use_container_width=True):
                if not up_label.strip():
                    st.error("Please provide an assessment label.")
                else:
                    dk = str(up_date)
                    data["assessments"][dk] = {"date":dk,"label":up_label,
                                               "scores":parsed,"notes":up_notes}
                    data["audit_log"].append({"action":"excel_upload","date":dk,
                                              "label":up_label,"states":len(parsed),
                                              "timestamp":datetime.now().isoformat()})
                    save_data(data)
                    st.success(f"✅ Saved '{up_label}' with {len(parsed)} states! Switch period in sidebar to view.")
                    st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# NEW ASSESSMENT (manual entry)
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed and saved.")
    with st.form("nf"):
        c1,c2 = st.columns(2)
        adate  = c1.date_input("Assessment Date", value=date.today(), max_value=date.today())
        alabel = c2.text_input("Label", placeholder="e.g. ARR FY 2026-27 / True-up FY 2024-25")
        anotes = st.text_area("Notes", placeholder="Key policy changes, data sources...")
        st.markdown("---")
        st.markdown("#### Scores per State / UT")
        prev = snapshot["scores"]
        new_scores = {}
        for state in sorted(BASELINE.keys()):
            p = prev.get(state, {})
            with st.expander(f"📍 {state}  ·  Last: {p.get('total',0):.1f}  ·  Grade {p.get('grade','—')}"):
                i1,i2,i3,i4,i5 = st.columns(5)
                n_ra = i1.number_input("RA (0-32)", 0.0,32.0, float(gv(p,"ra","resource_adequacy")),   0.5, key=f"{state}_ra")
                n_fv = i2.number_input("FV (0-25)", 0.0,25.0, float(gv(p,"fv","financial_viability")),  0.5, key=f"{state}_fv")
                n_el = i3.number_input("EL (0-23)", 0.0,23.0, float(gv(p,"el","ease_of_living")),       0.5, key=f"{state}_el")
                n_et = i4.number_input("ET (0-15)", 0.0,15.0, float(gv(p,"et","energy_transition")),    0.5, key=f"{state}_et")
                n_rg = i5.number_input("RG (0-5)",  0.0, 5.0, float(gv(p,"rg","regulatory_governance")),0.5, key=f"{state}_rg")
                n_tot = round(n_ra+n_fv+n_el+n_et+n_rg, 2)
                st.markdown(f"**→ Total: {n_tot} / 100 — Grade {get_grade(n_tot)}**")
                new_scores[state] = {"ra":n_ra,"fv":n_fv,"el":n_el,"et":n_et,"rg":n_rg,
                                     "total":n_tot,"grade":get_grade(n_tot)}
        if st.form_submit_button("💾 Save Assessment", type="primary", use_container_width=True):
            if not alabel.strip():
                st.error("Please enter a label.")
            else:
                dk = str(adate)
                data["assessments"][dk] = {"date":dk,"label":alabel,"scores":new_scores,"notes":anotes}
                data["audit_log"].append({"action":"new_assessment","date":dk,"label":alabel,
                                          "timestamp":datetime.now().isoformat()})
                save_data(data)
                st.success(f"✅ Saved '{alabel}' for {dk}!")
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# HISTORY
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📋 History":
    rows_h = []
    for d, snap in sorted(data["assessments"].items(), reverse=True):
        sc  = snap["scores"]
        avg = round(sum(v.get("total",0) for v in sc.values())/max(len(sc),1), 2)
        rows_h.append({"Date":d,"Label":snap["label"],"States":len(sc),"Avg Score":avg,
                       "Notes":snap.get("notes","")[:60]})
    st.dataframe(pd.DataFrame(rows_h), use_container_width=True, hide_index=True)
    if data["audit_log"]:
        st.markdown("#### 📋 Audit Log")
        st.dataframe(pd.DataFrame(data["audit_log"]), use_container_width=True, hide_index=True)
    st.markdown("---")
    deletable = [d for d in sorted(data["assessments"].keys()) if d != "2025-03-31"]
    if deletable:
        del_sel = st.selectbox("Delete an assessment (baseline protected)", deletable)
        if st.button("🗑️ Delete Selected", type="secondary"):
            del data["assessments"][del_sel]
            save_data(data)
            st.success(f"Deleted {del_sel}")
            st.rerun()
    else:
        st.info("Only the baseline exists. Add new assessments to manage them here.")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.caption("First Report: Rating Regulatory Performance of States & UTs | Power Foundation of India & REC Ltd. | Ministry of Power, GoI | Assessment cut-off: 31 March 2025")
