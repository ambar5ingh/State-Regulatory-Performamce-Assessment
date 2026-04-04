import sys
st.write(sys.executable)
import streamlit as st
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
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
    padding: 2rem 2.5rem; border-radius: 16px; color: white;
    margin-bottom: 1.8rem; border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 8px 32px rgba(13,27,75,0.25); position: relative; overflow: hidden;
}
.header-box h1 { margin: 0; font-family: 'Syne', sans-serif; font-size: 1.8rem; font-weight: 800; }
.header-box p  { margin: 0.4rem 0 0; opacity: 0.75; font-size: 0.82rem; }
.badge { display:inline-block; background:rgba(255,255,255,0.15); border:1px solid rgba(255,255,255,0.2);
         border-radius:20px; padding:3px 12px; font-size:0.72rem; margin:4px 2px 0; }
.kpi-card { background:white; border-radius:14px; padding:1.3rem 1.4rem; text-align:center;
            box-shadow:0 2px 12px rgba(0,0,0,0.06); border:1px solid #e8eaed; height:100%; }
.kpi-val  { font-family:'Syne',sans-serif; font-size:2.2rem; font-weight:800; line-height:1; }
.kpi-lbl  { font-size:0.73rem; color:#888; margin-top:4px; font-weight:500;
             text-transform:uppercase; letter-spacing:0.5px; }
.kpi-sub  { font-size:0.78rem; color:#555; margin-top:2px; }
.grade-pill { display:inline-block; padding:3px 14px; border-radius:20px; font-weight:700; font-size:0.82rem; }
.gA { background:#e8f5e9; color:#1b5e20; border:1px solid #a5d6a7; }
.gB { background:#e3f2fd; color:#0d47a1; border:1px solid #90caf9; }
.gC { background:#fff3e0; color:#bf360c; border:1px solid #ffcc80; }
.gD { background:#fce4ec; color:#880e4f; border:1px solid #f48fb1; }
.gE { background:#f3e5f5; color:#4a148c; border:1px solid #ce93d8; }
.param-block { background:white; border-left:4px solid #1a3a7c; border-radius:0 10px 10px 0;
               padding:1rem 1.4rem; margin-bottom:0.9rem; box-shadow:0 1px 6px rgba(0,0,0,0.05); }
.param-block .ptitle { font-weight:600; color:#0d1b4b; margin-bottom:8px; font-size:0.88rem; }
.state-scorecard { background:white; border-radius:16px; padding:2rem; text-align:center;
                   box-shadow:0 4px 20px rgba(0,0,0,0.08); border:1px solid #e8eaed; }
.info-banner { background:linear-gradient(90deg,#e8f5e9,#f1f8e9); border-left:4px solid #43a047;
               border-radius:0 10px 10px 0; padding:0.8rem 1.2rem; margin-bottom:1rem;
               font-size:0.85rem; color:#2e7d32; }
[data-testid="stSidebar"] { background: linear-gradient(180deg, #0d1b4b 0%, #1a3a7c 100%); }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"
GRADE_COLOR = {"A":"#1b5e20","B":"#0d47a1","C":"#bf360c","D":"#880e4f","E":"#4a148c"}
GRADE_BG    = {"A":"#e8f5e9","B":"#e3f2fd","C":"#fff3e0","D":"#fce4ec","E":"#f3e5f5"}
GRADE_CSS   = {"A":"gA","B":"gB","C":"gC","D":"gD","E":"gE"}

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
        "scores":scores,"notes":"First Report: Rating Regulatory Performance of States & UTs"
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

def parse_excel_csv(file) -> dict | None:
    """Accept CSV or Excel (if openpyxl available), return scores dict."""
    try:
        name = file.name.lower()
        if name.endswith(".csv"):
            xdf = pd.read_csv(file)
        else:
            try:
                xdf = pd.read_excel(file, engine="openpyxl")
            except Exception:
                st.error("Excel support unavailable. Please upload a CSV file instead.")
                return None
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
        st.error(f"File parsing error: {e}")
        return None

def make_csv_template():
    rows = [{"State/UT": st,
             "Resource Adequacy": b["ra"], "Financial Viability": b["fv"],
             "Ease of Living": b["el"], "Energy Transition": b["et"],
             "Regulatory Governance": b["rg"]} for st, b in BASELINE.items()]
    return pd.DataFrame(rows).to_csv(index=False).encode()

# ─── MATPLOTLIB CHARTS ────────────────────────────────────────────────────────
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "white"})

def chart_rankings(df_sorted):
    n = len(df_sorted)
    fig, ax = plt.subplots(figsize=(10, max(6, n * 0.32)))
    colors = [GRADE_COLOR[g] for g in df_sorted["Grade"]]
    bars = ax.barh(range(n), df_sorted["Total"], color=colors, height=0.65, zorder=2)
    ax.set_yticks(range(n))
    ax.set_yticklabels(df_sorted["State/UT"], fontsize=8.5)
    ax.set_xlim(0, 110)
    ax.set_xlabel("Score (out of 100)")
    ax.set_title("All States & UTs — Performance Ranking", fontweight="bold", pad=12)
    ax.invert_yaxis()
    ax.axvline(85, color=GRADE_COLOR["A"], linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axvline(65, color=GRADE_COLOR["B"], linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axvline(50, color=GRADE_COLOR["C"], linestyle="--", linewidth=0.8, alpha=0.6)
    ax.axvline(35, color=GRADE_COLOR["D"], linestyle="--", linewidth=0.8, alpha=0.6)
    for i, (bar, val) in enumerate(zip(bars, df_sorted["Total"])):
        ax.text(val + 1, i, f"{val:.1f}", va="center", fontsize=7.5, color="#333")
    legend = [mpatches.Patch(color=GRADE_COLOR[g], label=f"Grade {g}") for g in "ABCDE"]
    ax.legend(handles=legend, loc="lower right", fontsize=8, framealpha=0.8)
    ax.grid(axis="x", color="#f0f0f0", zorder=0)
    fig.tight_layout()
    return fig

def chart_grade_donut(gc):
    fig, ax = plt.subplots(figsize=(4, 4))
    labels = [f"Grade {g}" for g in gc.index]
    colors = [GRADE_BG[g] for g in gc.index]
    wedges, texts, autotexts = ax.pie(
        gc.values, labels=labels, colors=colors, autopct="%d", startangle=90,
        wedgeprops=dict(width=0.5, edgecolor="white", linewidth=2),
        textprops={"fontsize": 9},
    )
    for at, g in zip(autotexts, gc.index):
        at.set_color(GRADE_COLOR[g]); at.set_fontweight("bold")
    ax.set_title("Grade Distribution", fontweight="bold")
    fig.tight_layout()
    return fig

def chart_region_bar(df):
    rdf = df.groupby("Region")["Total"].mean().sort_values(ascending=False)
    fig, ax = plt.subplots(figsize=(5, 3.5))
    norm = plt.Normalize(rdf.min(), rdf.max())
    colors = [plt.cm.RdYlGn(norm(v)) for v in rdf.values]
    bars = ax.bar(rdf.index, rdf.values, color=colors, edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, rdf.values):
        ax.text(bar.get_x() + bar.get_width()/2, val + 0.5, f"{val:.1f}",
                ha="center", va="bottom", fontsize=8, fontweight="bold")
    ax.set_title("Avg Score by Region", fontweight="bold")
    ax.set_ylabel("Average Score")
    ax.set_ylim(0, 105)
    plt.xticks(rotation=30, ha="right", fontsize=8)
    ax.grid(axis="y", color="#f0f0f0")
    fig.tight_layout()
    return fig

def chart_heatmap(df):
    heat = df.set_index("State/UT")[["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]].copy()
    for col, mx in zip(heat.columns, [32,25,23,15,5]):
        heat[col] = (heat[col]/mx*100).round(1)
    fig, ax = plt.subplots(figsize=(9, max(8, len(heat)*0.28)))
    im = ax.imshow(heat.values, cmap="RdYlGn", aspect="auto", vmin=0, vmax=100)
    ax.set_xticks(range(len(heat.columns)))
    ax.set_xticklabels(["Res.\nAdequacy","Fin.\nViability","Ease of\nLiving","Energy\nTransition","Reg.\nGovernance"], fontsize=8)
    ax.set_yticks(range(len(heat)))
    ax.set_yticklabels(heat.index, fontsize=7.5)
    for i in range(len(heat)):
        for j in range(len(heat.columns)):
            val = heat.values[i, j]
            ax.text(j, i, f"{val:.0f}%", ha="center", va="center",
                    fontsize=6.5, color="black" if 30 < val < 80 else "white")
    plt.colorbar(im, ax=ax, label="% of Max Marks", shrink=0.6)
    ax.set_title("Parameter Achievement Heatmap (% of Max Marks)", fontweight="bold", pad=12)
    fig.tight_layout()
    return fig

def chart_radar(state_name, vals, maxes, color="#1a3a7c"):
    labels = ["Resource\nAdequacy","Financial\nViability","Ease of\nLiving","Energy\nTransition","Regulatory\nGovernance"]
    pcts = [v/m*100 for v,m in zip(vals,maxes)]
    N = len(labels)
    angles = [n/N*2*np.pi for n in range(N)] + [0]
    pcts_c = pcts + [pcts[0]]
    fig, ax = plt.subplots(figsize=(4, 4), subplot_kw=dict(polar=True))
    ax.plot(angles, pcts_c, color=color, linewidth=2)
    ax.fill(angles, pcts_c, color=color, alpha=0.15)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25%","50%","75%","100%"], fontsize=6)
    ax.set_title(state_name, fontweight="bold", pad=15, fontsize=10)
    ax.grid(color="#e0e0e0")
    fig.tight_layout()
    return fig

def chart_compare_radar(sa_name, va, sb_name, vb):
    keys   = ["ra","fv","el","et","rg"]
    maxes  = [32,25,23,15,5]
    labels = ["Resource\nAdequacy","Financial\nViability","Ease of\nLiving","Energy\nTransition","Regulatory\nGovernance"]
    pa = [va[k]/m*100 for k,m in zip(keys,maxes)]
    pb = [vb[k]/m*100 for k,m in zip(keys,maxes)]
    N = len(labels)
    angles = [n/N*2*np.pi for n in range(N)] + [0]
    fig, ax = plt.subplots(figsize=(5, 4.5), subplot_kw=dict(polar=True))
    for pcts, name, color in [(pa, sa_name, "#1a3a7c"), (pb, sb_name, "#c62828")]:
        pcts_c = pcts + [pcts[0]]
        ax.plot(angles, pcts_c, color=color, linewidth=2, label=name)
        ax.fill(angles, pcts_c, color=color, alpha=0.1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=7.5)
    ax.set_ylim(0, 100)
    ax.set_yticks([25, 50, 75, 100])
    ax.set_yticklabels(["25%","50%","75%","100%"], fontsize=6)
    ax.legend(loc="lower center", bbox_to_anchor=(0.5, -0.18), fontsize=8, ncol=2)
    ax.set_title("Parameter Comparison", fontweight="bold", pad=15)
    ax.grid(color="#e0e0e0")
    fig.tight_layout()
    return fig

def chart_scatter(df):
    fig, ax = plt.subplots(figsize=(8, 5))
    for grade in "ABCDE":
        sub = df[df["Grade"]==grade]
        ax.scatter(sub["Fin. Viability"], sub["Res. Adequacy"],
                   s=sub["Total"]*3, color=GRADE_COLOR[grade], alpha=0.75,
                   edgecolors="white", linewidth=0.8, label=f"Grade {grade}", zorder=3)
    for _, row in df.iterrows():
        ax.annotate(row["State/UT"], (row["Fin. Viability"], row["Res. Adequacy"]),
                    fontsize=5.5, ha="center", va="bottom", color="#333")
    ax.set_xlabel("Financial Viability (out of 25)")
    ax.set_ylabel("Resource Adequacy (out of 32)")
    ax.set_title("Resource Adequacy vs Financial Viability\n(bubble size = total score)", fontweight="bold")
    ax.legend(fontsize=8)
    ax.grid(color="#f0f0f0", zorder=0)
    fig.tight_layout()
    return fig

def chart_type_box(df):
    fig, ax = plt.subplots(figsize=(5, 3.5))
    for i, (typ, color) in enumerate([("State","#1a3a7c"),("UT","#c62828")]):
        vals = df[df["Type"]==typ]["Total"].values
        bp = ax.boxplot(vals, positions=[i], widths=0.5, patch_artist=True,
                        boxprops=dict(facecolor=color, alpha=0.4),
                        medianprops=dict(color=color, linewidth=2),
                        whiskerprops=dict(color=color), capprops=dict(color=color))
        ax.scatter(np.random.normal(i, 0.05, len(vals)), vals, color=color, alpha=0.6, s=20, zorder=3)
    ax.set_xticks([0,1]); ax.set_xticklabels(["States","Union Territories"])
    ax.set_ylabel("Total Score"); ax.set_title("States vs Union Territories", fontweight="bold")
    ax.set_ylim(0,105); ax.grid(axis="y", color="#f0f0f0")
    fig.tight_layout()
    return fig

def chart_trend(tdf, param):
    fig, ax = plt.subplots(figsize=(9, 4))
    palette = ["#1a3a7c","#c62828","#2e7d32","#f57c00","#6a1b9a","#00838f","#558b2f","#4e342e"]
    for i, (state, grp) in enumerate(tdf.groupby("State/UT")):
        grp = grp.sort_values("Date")
        ax.plot(grp["Date"], grp[param], marker="o", linewidth=2.2,
                color=palette[i % len(palette)], label=state, markersize=6)
    ax.set_title(f"Trend: {param}", fontweight="bold")
    ax.set_ylabel(param)
    ax.legend(fontsize=7, loc="best", ncol=2)
    ax.grid(color="#f0f0f0")
    plt.xticks(rotation=20, ha="right", fontsize=8)
    fig.tight_layout()
    return fig

def chart_delta(chg_df):
    chg_df = chg_df.sort_values("Δ")
    colors = [GRADE_COLOR["A"] if v >= 0 else GRADE_COLOR["D"] for v in chg_df["Δ"]]
    fig, ax = plt.subplots(figsize=(10, 4))
    bars = ax.bar(range(len(chg_df)), chg_df["Δ"], color=colors, edgecolor="white", linewidth=0.5)
    ax.set_xticks(range(len(chg_df)))
    ax.set_xticklabels(chg_df["State/UT"], rotation=45, ha="right", fontsize=7)
    ax.axhline(0, color="#333", linewidth=0.8)
    ax.set_title("Score Change: First → Latest Assessment", fontweight="bold")
    ax.set_ylabel("Δ Score")
    ax.grid(axis="y", color="#f0f0f0")
    fig.tight_layout()
    return fig

def chart_compare_bar(sa_name, va, sb_name, vb):
    keys   = ["ra","fv","el","et","rg"]
    maxes  = [32,25,23,15,5]
    labels = ["Res.\nAdequacy","Fin.\nViability","Ease of\nLiving","Energy\nTransition","Reg.\nGovernance"]
    pa = [va[k]/m*100 for k,m in zip(keys,maxes)]
    pb = [vb[k]/m*100 for k,m in zip(keys,maxes)]
    x = np.arange(len(labels)); w = 0.35
    fig, ax = plt.subplots(figsize=(8, 4))
    b1 = ax.bar(x - w/2, pa, w, label=sa_name, color="#1a3a7c", alpha=0.85)
    b2 = ax.bar(x + w/2, pb, w, label=sb_name, color="#c62828", alpha=0.85)
    for bars in [b1, b2]:
        for bar in bars:
            ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1,
                    f"{bar.get_height():.0f}%", ha="center", fontsize=7.5)
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 115); ax.set_ylabel("% of Max Marks")
    ax.set_title("Parameter Comparison (% of Max)", fontweight="bold")
    ax.legend(); ax.grid(axis="y", color="#f0f0f0")
    fig.tight_layout()
    return fig

# ─── LOAD ─────────────────────────────────────────────────────────────────────
data = load_data()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem">
      <div style="font-size:2.5rem">⚡</div>
      <div style="font-family:'Syne',sans-serif;font-size:1rem;font-weight:700">Regulatory Performance</div>
      <div style="font-size:0.72rem;opacity:0.6;margin-top:2px">States & Union Territories</div>
    </div>""", unsafe_allow_html=True)
    st.markdown("---")
    page = st.radio("Navigate", [
        "📊 Dashboard", "🔍 State Profile", "📈 Trends",
        "⚖️ Compare", "📤 Upload File", "📝 New Assessment", "📋 History",
    ], label_visibility="collapsed")
    st.markdown("---")
    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox("📅 Assessment Period", dates,
                            format_func=lambda d: data["assessments"][d]["label"])
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

    c1,c2,c3,c4,c5,c6 = st.columns(6)
    kpis = [
        (len(df),            "#0d1b4b",          "States & UTs",  ""),
        (gc.get("A",0),      GRADE_COLOR["A"],    "Grade A",       "≥ 85 marks"),
        (gc.get("B",0),      GRADE_COLOR["B"],    "Grade B",       "65–84 marks"),
        (gc.get("C",0),      GRADE_COLOR["C"],    "Grade C",       "50–64 marks"),
        (gc.get("D",0)+gc.get("E",0), GRADE_COLOR["D"], "Grade D/E", "< 50 marks"),
        (f"{avg:.1f}",       "#555",              "National Avg",  "out of 100"),
    ]
    for col, (val, color, lbl, sub) in zip([c1,c2,c3,c4,c5,c6], kpis):
        with col:
            st.markdown(f"""<div class="kpi-card">
              <div class="kpi-val" style="color:{color}">{val}</div>
              <div class="kpi-lbl">{lbl}</div>
              {'<div class="kpi-sub">'+sub+'</div>' if sub else ''}
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Rankings", "📊 Charts", "🔬 Deep Dive", "🗺️ Heatmap", "📋 Table"])

    with tab1:
        col_f1, col_f2 = st.columns([3,1])
        search      = col_f1.text_input("🔍 Search", placeholder="Filter by name...", label_visibility="collapsed")
        filter_type = col_f2.selectbox("Type", ["All","State","UT"], label_visibility="collapsed")
        fdf = df.copy()
        if search: fdf = fdf[fdf["State/UT"].str.contains(search, case=False)]
        if filter_type != "All": fdf = fdf[fdf["Type"]==filter_type]
        st.pyplot(chart_rankings(fdf.sort_values("Total", ascending=True)), use_container_width=True)

    with tab2:
        r1c1, r1c2 = st.columns(2)
        with r1c1: st.pyplot(chart_grade_donut(gc), use_container_width=True)
        with r1c2: st.pyplot(chart_region_bar(df), use_container_width=True)
        r2c1, r2c2 = st.columns(2)
        with r2c1: st.pyplot(chart_type_box(df), use_container_width=True)

    with tab3:
        st.pyplot(chart_scatter(df), use_container_width=True)

    with tab4:
        st.pyplot(chart_heatmap(df), use_container_width=True)

    with tab5:
        disp = df.copy(); disp.insert(0,"Rank",disp.index)
        st.dataframe(disp.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100),
                     use_container_width=True, height=600)
        st.download_button("⬇️ Download CSV", df.to_csv(index=False).encode(),
                           "regulatory_rankings.csv", mime="text/csv")

# ══════════════════════════════════════════════════════════════════════════════
# STATE PROFILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "🔍 State Profile":
    c1, c2 = st.columns([2,1])
    sel  = c1.selectbox("Select State / UT", sorted(scores.keys()))
    show_peers = c2.checkbox("Show regional peers", value=False)

    s     = scores[sel]
    b     = BASELINE.get(sel, {})
    ra    = gv(s,"ra","resource_adequacy")
    fv    = gv(s,"fv","financial_viability")
    el    = gv(s,"el","ease_of_living")
    et    = gv(s,"et","energy_transition")
    rg    = gv(s,"rg","regulatory_governance")
    total = s.get("total", 0)
    grade = s.get("grade", get_grade(total))
    rank_list = df[df["State/UT"]==sel].index.tolist()
    rank_str  = str(rank_list[0]) if rank_list else "—"

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown(f"""<div class="state-scorecard">
          <div style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;color:#0d1b4b">{sel}</div>
          <div style="margin:8px 0">{grade_pill(grade)}</div>
          <div style="font-size:0.8rem;color:#888;margin-bottom:8px">Rank <b>{rank_str}</b> of {len(df)}</div>
          <div style="font-size:3rem;font-weight:800;color:{GRADE_COLOR[grade]};font-family:'Syne',sans-serif">{total}</div>
          <div style="color:#888;font-size:0.78rem">out of 100</div>
          <hr>
          <div style="font-size:0.78rem;color:#666">🗺️ {b.get('region','—')} &nbsp;|&nbsp; 🏛️ {b.get('type','—')}</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        vals  = [ra, fv, el, et, rg]
        maxes = [32, 25, 23, 15,  5]
        st.pyplot(chart_radar(sel, vals, maxes, GRADE_COLOR[grade]), use_container_width=True)

    st.markdown("#### Parameter Breakdown")
    p1, p2 = st.columns(2)
    for i, (label, val, mx) in enumerate([("Resource Adequacy",ra,32),("Financial Viability",fv,25),
                                           ("Ease of Living",el,23),("Energy Transition",et,15),
                                           ("Regulatory Governance",rg,5)]):
        pct = val/mx*100; col = score_color(pct)
        target = p1 if i % 2 == 0 else p2
        with target:
            st.markdown(f"""<div class="param-block">
              <div class="ptitle">{label}
                <span style="float:right;color:{col};font-weight:700">{val} / {mx} &nbsp; ({pct:.0f}%)</span>
              </div>
              <div style="background:#e8eaed;border-radius:6px;height:10px">
                <div style="width:{int(pct)}%;background:{col};height:10px;border-radius:6px"></div>
              </div></div>""", unsafe_allow_html=True)

    if show_peers:
        region = b.get("region","")
        peers  = df[df["Region"]==region].sort_values("Total", ascending=False)
        st.markdown(f"#### 🌏 Regional Peers — {region}")
        fig, ax = plt.subplots(figsize=(8, 3))
        colors = [GRADE_COLOR[g] for g in peers["Grade"]]
        bars = ax.bar(peers["State/UT"], peers["Total"], color=colors, edgecolor="white")
        for bar, val in zip(bars, peers["Total"]):
            ax.text(bar.get_x()+bar.get_width()/2, val+0.5, f"{val:.1f}", ha="center", fontsize=8)
        ax.set_ylim(0,110); ax.set_title(f"{region} Region Rankings", fontweight="bold")
        plt.xticks(rotation=25, ha="right", fontsize=8); ax.grid(axis="y", color="#f0f0f0")
        fig.tight_layout(); st.pyplot(fig, use_container_width=True)

    history = [{"Assessment": snap["label"], "Score": snap["scores"].get(sel,{}).get("total",0)}
               for d, snap in sorted(data["assessments"].items()) if sel in snap["scores"]]
    if len(history) > 1:
        st.markdown("---")
        hist_df = pd.DataFrame(history)
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.plot(hist_df["Assessment"], hist_df["Score"], marker="o", color=GRADE_COLOR[grade],
                linewidth=2.5, markersize=8)
        ax.set_ylim(0, 105); ax.set_title(f"Score History — {sel}", fontweight="bold")
        plt.xticks(rotation=20, ha="right", fontsize=8); ax.grid(color="#f0f0f0")
        fig.tight_layout(); st.pyplot(fig, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    if len(data["assessments"]) < 2:
        st.info("ℹ️ Add at least 2 assessments to see trends.")
    else:
        c1, c2 = st.columns([3,1])
        sel_states = c1.multiselect("Select States/UTs", sorted(BASELINE.keys()),
                                    default=["Punjab","Karnataka","Uttar Pradesh","Delhi","Tripura"])
        param = c2.selectbox("Parameter", ["Total Score","Res. Adequacy","Fin. Viability",
                                            "Ease of Living","Energy Transition","Reg. Governance"])
        rows = []
        for d, snap in sorted(data["assessments"].items()):
            for stn in sel_states:
                sc = snap["scores"].get(stn, {})
                if sc:
                    rows.append({"Date":d,"State/UT":stn,
                                 "Total Score":sc.get("total",0),
                                 "Res. Adequacy":gv(sc,"ra","resource_adequacy"),
                                 "Fin. Viability":gv(sc,"fv","financial_viability"),
                                 "Ease of Living":gv(sc,"el","ease_of_living"),
                                 "Energy Transition":gv(sc,"et","energy_transition"),
                                 "Reg. Governance":gv(sc,"rg","regulatory_governance")})
        if rows:
            tdf = pd.DataFrame(rows)
            st.pyplot(chart_trend(tdf, param), use_container_width=True)
            all_d = sorted(data["assessments"].keys())
            if len(all_d) >= 2:
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
                                    "Direction":"▲ Improved" if delta>0 else("▼ Declined" if delta<0 else "→ Same")})
                chg_df = pd.DataFrame(chg).sort_values("Δ", ascending=False)
                st.pyplot(chart_delta(chg_df), use_container_width=True)
                st.dataframe(chg_df, use_container_width=True, hide_index=True)

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

        cc1, cc2 = st.columns(2)
        for col, name, v in [(cc1,sa_name,va),(cc2,sb_name,vb)]:
            with col:
                g = v["grade"]
                winner = "🏆 " if v["total"] > (vb["total"] if name==sa_name else va["total"]) else ""
                st.markdown(f"""<div class="state-scorecard">
                  <div style="font-size:1.1rem;font-family:'Syne',sans-serif;font-weight:800;color:#0d1b4b">{winner}{name}</div>
                  <div style="margin:8px 0">{grade_pill(g)}</div>
                  <div style="font-size:3rem;font-weight:800;color:{GRADE_COLOR[g]};font-family:'Syne',sans-serif">{v['total']}</div>
                  <div style="color:#888;font-size:0.78rem">out of 100</div>
                </div>""", unsafe_allow_html=True)

        r1, r2 = st.columns([3,2])
        with r1: st.pyplot(chart_compare_radar(sa_name, va, sb_name, vb), use_container_width=True)
        with r2:
            cmp_rows = []
            for label, key, mx in [("Resource Adequacy","ra",32),("Financial Viability","fv",25),
                                    ("Ease of Living","el",23),("Energy Transition","et",15),
                                    ("Regulatory Governance","rg",5),("TOTAL","total",100)]:
                av, bv = va[key], vb[key]
                win = f"✅ {sa_name}" if av>bv else (f"✅ {sb_name}" if bv>av else "Tied")
                cmp_rows.append({"Parameter":label, sa_name:f"{av}/{mx}", sb_name:f"{bv}/{mx}", "Better":win})
            st.dataframe(pd.DataFrame(cmp_rows), use_container_width=True, hide_index=True)
        st.pyplot(chart_compare_bar(sa_name, va, sb_name, vb), use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# UPLOAD FILE
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📤 Upload File":
    st.markdown("""<div class="info-banner">
      ✅ Upload a <b>CSV file</b> with assessment data to create a new assessment period.
      Required columns: <b>State/UT</b>, <b>Resource Adequacy</b>, <b>Financial Viability</b>,
      <b>Ease of Living</b>, <b>Energy Transition</b>, <b>Regulatory Governance</b>
    </div>""", unsafe_allow_html=True)

    st.download_button("⬇️ Download CSV Template", make_csv_template(),
                       "assessment_template.csv", mime="text/csv", use_container_width=False)

    st.markdown("---")
    uploaded = st.file_uploader("📂 Upload CSV (or Excel if openpyxl is installed)",
                                type=["csv","xlsx","xls"])
    if uploaded:
        parsed = parse_excel_csv(uploaded)
        if parsed is None:
            st.error("❌ Could not parse file. Check column names match the template.")
        else:
            st.success(f"✅ Parsed {len(parsed)} states/UTs successfully!")
            prev_rows = [{"State/UT":st,"RA":sc["ra"],"FV":sc["fv"],"EL":sc["el"],
                          "ET":sc["et"],"RG":sc["rg"],"Total":sc["total"],"Grade":sc["grade"]}
                         for st, sc in parsed.items()]
            prev_df = pd.DataFrame(prev_rows).sort_values("Total", ascending=False)
            st.dataframe(prev_df.style.background_gradient(subset=["Total"], cmap="RdYlGn", vmin=0, vmax=100),
                         use_container_width=True, height=300)

            c1, c2 = st.columns(2)
            up_date  = c1.date_input("Assessment Date", value=date.today())
            up_label = c2.text_input("Assessment Label", placeholder="e.g. ARR FY 2026-27")
            up_notes = st.text_area("Notes", placeholder="Source, methodology...")

            if st.button("💾 Save Assessment", type="primary", use_container_width=True):
                if not up_label.strip():
                    st.error("Please provide a label.")
                else:
                    dk = str(up_date)
                    data["assessments"][dk] = {"date":dk,"label":up_label,"scores":parsed,"notes":up_notes}
                    data["audit_log"].append({"action":"file_upload","date":dk,"label":up_label,
                                              "states":len(parsed),"timestamp":datetime.now().isoformat()})
                    save_data(data)
                    st.success(f"✅ Saved '{up_label}' with {len(parsed)} states!")
                    st.balloons()

# ══════════════════════════════════════════════════════════════════════════════
# NEW ASSESSMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "📝 New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed.")
    with st.form("nf"):
        c1, c2 = st.columns(2)
        adate  = c1.date_input("Assessment Date", value=date.today(), max_value=date.today())
        alabel = c2.text_input("Label", placeholder="e.g. ARR FY 2026-27")
        anotes = st.text_area("Notes", placeholder="Key policy changes, data sources...")
        st.markdown("---")
        prev = snapshot["scores"]; new_scores = {}
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
                save_data(data); st.success(f"✅ Saved '{alabel}'!"); st.rerun()

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
        del_sel = st.selectbox("Delete assessment (baseline protected)", deletable)
        if st.button("🗑️ Delete", type="secondary"):
            del data["assessments"][del_sel]; save_data(data)
            st.success(f"Deleted {del_sel}"); st.rerun()
    else:
        st.info("Only the baseline exists. Add new assessments to manage them here.")

st.markdown("---")
st.caption("First Report: Rating Regulatory Performance of States & UTs | Power Foundation of India & REC Ltd. | Ministry of Power, GoI")
