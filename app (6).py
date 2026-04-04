import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date

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
.header-box {
    background: linear-gradient(135deg, #1a237e, #1565c0);
    padding: 1.8rem 2rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;
}
.header-box h1 { margin: 0; font-size: 1.7rem; }
.header-box p  { margin: 0.3rem 0 0; opacity: 0.85; font-size: 0.88rem; }
.kpi-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap; }
.kpi { flex: 1; min-width: 130px; background: white; border: 1px solid #e0e0e0;
       border-radius: 10px; padding: 1rem 1.2rem; text-align: center;
       box-shadow: 0 2px 6px rgba(0,0,0,0.06); }
.kpi .val { font-size: 2rem; font-weight: 700; }
.kpi .lbl { font-size: 0.75rem; color: #666; margin-top: 2px; }
.bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 7px; }
.bar-label { width: 200px; font-size: 0.82rem; text-align: right; white-space: nowrap;
             overflow: hidden; text-overflow: ellipsis; }
.bar-track { flex: 1; background: #e0e0e0; border-radius: 6px; height: 18px; }
.bar-fill  { height: 18px; border-radius: 6px; }
.bar-score { width: 55px; font-size: 0.8rem; font-weight: 600; text-align: left; }
.grade-pill { display: inline-block; padding: 2px 12px; border-radius: 20px; font-weight: 700; font-size: 0.85rem; }
.gA { background:#e8f5e9; color:#2e7d32; }
.gB { background:#e3f2fd; color:#1565c0; }
.gC { background:#fff3e0; color:#e65100; }
.gD { background:#fce4ec; color:#b71c1c; }
.gE { background:#f3e5f5; color:#6a1b9a; }
.param-block { background:#f8f9fa; border-left:4px solid #1565c0;
               border-radius:0 8px 8px 0; padding:0.9rem 1.2rem; margin-bottom:0.8rem; }
.param-block .ptitle { font-weight:700; color:#1a237e; margin-bottom:6px; font-size:0.9rem; }
</style>
""", unsafe_allow_html=True)

# ─── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_FILE = "assessment_data.json"
GRADE_COLOR = {"A":"#2e7d32","B":"#1565c0","C":"#e65100","D":"#b71c1c","E":"#6a1b9a"}
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
            "Res. Adequacy": gv(s,"ra","resource_adequacy"),
            "Fin. Viability": gv(s,"fv","financial_viability"),
            "Ease of Living": gv(s,"el","ease_of_living"),
            "Energy Transition": gv(s,"et","energy_transition"),
            "Reg. Governance": gv(s,"rg","regulatory_governance"),
            "Total": s.get("total", 0), "Grade": s.get("grade","E"),
        })
    df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
    df.index += 1
    return df

# ─── LOAD ─────────────────────────────────────────────────────────────────────
data     = load_data()

with st.sidebar:
    st.markdown("### ⚡ Navigation")
    page = st.radio("", ["📊 Dashboard","🔍 State Profile","📝 New Assessment",
                         "📈 Trends","⚖️ Compare","📋 History"], label_visibility="collapsed")
    st.markdown("---")
    dates    = sorted(data["assessments"].keys(), reverse=True)
    sel_date = st.selectbox("Period", dates,
                            format_func=lambda d: data["assessments"][d]["label"],
                            label_visibility="collapsed")

snapshot = data["assessments"][sel_date]
scores   = snapshot["scores"]
df       = build_df(scores)

st.markdown("""
<div class="header-box">
  <h1>⚡ Regulatory Performance Rating — States &amp; UTs</h1>
  <p>Power Foundation of India &amp; REC Ltd. | Ministry of Power, GoI |
  Resource Adequacy · Financial Viability · Ease of Living · Energy Transition · Regulatory Governance</p>
</div>""", unsafe_allow_html=True)

# ══════ DASHBOARD ════════════════════════════════════════════════════════════
if page == "📊 Dashboard":
    gc  = df["Grade"].value_counts()
    avg = df["Total"].mean()
    st.markdown(f"""
    <div class="kpi-row">
      <div class="kpi"><div class="val">{len(df)}</div><div class="lbl">States &amp; UTs</div></div>
      <div class="kpi"><div class="val" style="color:{GRADE_COLOR['A']}">{gc.get('A',0)}</div><div class="lbl">Grade A (≥85)</div></div>
      <div class="kpi"><div class="val" style="color:{GRADE_COLOR['B']}">{gc.get('B',0)}</div><div class="lbl">Grade B (65-84)</div></div>
      <div class="kpi"><div class="val" style="color:{GRADE_COLOR['C']}">{gc.get('C',0)}</div><div class="lbl">Grade C (50-64)</div></div>
      <div class="kpi"><div class="val" style="color:{GRADE_COLOR['D']}">{gc.get('D',0)+gc.get('E',0)}</div><div class="lbl">Grade D/E (&lt;50)</div></div>
      <div class="kpi"><div class="val">{avg:.1f}</div><div class="lbl">National Avg</div></div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "📊 Charts", "🗺️ Heatmap"])

    with tab1:
        disp = df.copy()
        disp.insert(0,"Rank", disp.index)
        st.dataframe(disp, use_container_width=True, height=600)

    with tab2:
        st.markdown("#### All States/UTs – Score Bar")
        sdf = df.sort_values("Total", ascending=True)
        bars = ""
        for _, row in sdf.iterrows():
            col = GRADE_COLOR[row["Grade"]]
            bars += (f'<div class="bar-row">'
                     f'<div class="bar-label" title="{row["State/UT"]}">{row["State/UT"]}</div>'
                     f'<div class="bar-track"><div class="bar-fill" style="width:{row["Total"]}%;background:{col}"></div></div>'
                     f'<div class="bar-score" style="color:{col}">{row["Total"]:.1f}</div></div>')
        st.markdown(bars, unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### Grade Count")
            st.bar_chart(pd.DataFrame({"Count": gc}))
        with c2:
            st.markdown("#### Avg Score by Region")
            rdf = df.groupby("Region")["Total"].mean().sort_values(ascending=False)
            st.bar_chart(rdf)

    with tab3:
        st.markdown("#### Achievement % vs Max Marks (green = better)")
        heat = df.set_index("State/UT")[["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"]].copy()
        heat["Res. Adequacy"]    = (heat["Res. Adequacy"]    / 32 * 100).round(1)
        heat["Fin. Viability"]   = (heat["Fin. Viability"]   / 25 * 100).round(1)
        heat["Ease of Living"]   = (heat["Ease of Living"]   / 23 * 100).round(1)
        heat["Energy Transition"]= (heat["Energy Transition"]/ 15 * 100).round(1)
        heat["Reg. Governance"]  = (heat["Reg. Governance"]  /  5 * 100).round(1)
        st.dataframe(heat.style.background_gradient(cmap="RdYlGn", vmin=0, vmax=100),
                     use_container_width=True, height=700)

# ══════ STATE PROFILE ════════════════════════════════════════════════════════
elif page == "🔍 State Profile":
    sel   = st.selectbox("Select State / UT", sorted(scores.keys()))
    s     = scores[sel]
    b     = BASELINE.get(sel, {})
    ra    = gv(s,"ra","resource_adequacy")
    fv    = gv(s,"fv","financial_viability")
    el    = gv(s,"el","ease_of_living")
    et    = gv(s,"et","energy_transition")
    rg    = gv(s,"rg","regulatory_governance")
    total = s.get("total", 0)
    grade = s.get("grade", get_grade(total))
    gc    = GRADE_COLOR[grade]
    rank_list = df[df["State/UT"]==sel].index.tolist()
    rank_str  = str(rank_list[0]) if rank_list else "—"

    col1, col2 = st.columns([1,2])
    with col1:
        st.markdown(f"""
        <div style="background:white;border:1px solid #ddd;border-radius:12px;padding:1.5rem;text-align:center;box-shadow:0 2px 8px rgba(0,0,0,0.07)">
          <div style="font-size:1.2rem;font-weight:700">{sel}</div>
          <div style="margin:6px 0">{grade_pill(grade)}</div>
          <div style="font-size:3rem;font-weight:800;color:{gc}">{total}</div>
          <div style="color:#888;font-size:0.8rem">out of 100</div>
          <hr>
          <div style="font-size:0.82rem;color:#555">Rank <b>{rank_str}</b> of {len(df)}<br>
          Region: <b>{b.get('region','—')}</b> | Type: <b>{b.get('type','—')}</b></div>
        </div>""", unsafe_allow_html=True)
    with col2:
        for label, val, mx in [("Resource Adequacy",ra,32),("Financial Viability",fv,25),
                                ("Ease of Living",el,23),("Energy Transition",et,15),
                                ("Regulatory Governance",rg,5)]:
            pct = val/mx*100
            col = score_color(pct)
            st.markdown(f"""
            <div class="param-block">
              <div class="ptitle">{label} &nbsp;
                <span style="color:{col}">{val} / {mx} &nbsp; ({pct:.0f}%)</span>
              </div>
              <div style="background:#e0e0e0;border-radius:6px;height:12px">
                <div style="width:{int(pct)}%;background:{col};height:12px;border-radius:6px"></div>
              </div>
            </div>""", unsafe_allow_html=True)

    history = [{"Assessment": snap["label"], "Score": snap["scores"].get(sel,{}).get("total",0)}
               for d, snap in sorted(data["assessments"].items())
               if sel in snap["scores"]]
    if len(history) > 1:
        st.markdown("---")
        st.markdown("#### 📈 Score History")
        st.line_chart(pd.DataFrame(history).set_index("Assessment"))

# ══════ NEW ASSESSMENT ═══════════════════════════════════════════════════════
elif page == "📝 New Assessment":
    st.info("Enter updated scores for each State/UT. Totals are auto-computed and saved locally.")
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

# ══════ TRENDS ═══════════════════════════════════════════════════════════════
elif page == "📈 Trends":
    if len(data["assessments"]) < 2:
        st.warning("Add at least 2 assessments via '📝 New Assessment' to see trends.")
    else:
        sel_states = st.multiselect("Select States/UTs", sorted(BASELINE.keys()),
                                    default=["Punjab","Karnataka","Uttar Pradesh","Delhi","Tripura"])
        rows = []
        for d, snap in sorted(data["assessments"].items()):
            for st_name in sel_states:
                sc = snap["scores"].get(st_name, {})
                if sc:
                    rows.append({"Date":d, "State/UT":st_name,
                                 "Total Score": sc.get("total",0),
                                 "Res. Adequacy": gv(sc,"ra","resource_adequacy"),
                                 "Fin. Viability": gv(sc,"fv","financial_viability"),
                                 "Ease of Living": gv(sc,"el","ease_of_living"),
                                 "Energy Transition": gv(sc,"et","energy_transition"),
                                 "Reg. Governance": gv(sc,"rg","regulatory_governance")})
        if rows:
            tdf  = pd.DataFrame(rows)
            pvt  = tdf.pivot(index="Date", columns="State/UT", values="Total Score")
            st.markdown("#### Total Score Trend")
            st.line_chart(pvt)
            param = st.selectbox("Parameter drill-down",
                                 ["Res. Adequacy","Fin. Viability","Ease of Living","Energy Transition","Reg. Governance"])
            pvt2 = tdf.pivot(index="Date", columns="State/UT", values=param)
            st.line_chart(pvt2)

            all_d = sorted(data["assessments"].keys())
            if len(all_d) >= 2:
                st.markdown("#### Change: First vs Latest")
                chg = []
                for state in sorted(BASELINE.keys()):
                    s1 = data["assessments"][all_d[0]]["scores"].get(state,{})
                    s2 = data["assessments"][all_d[-1]]["scores"].get(state,{})
                    if s1 and s2:
                        delta = round(s2.get("total",0)-s1.get("total",0), 2)
                        chg.append({"State/UT":state, f"Score ({all_d[0]})":s1.get("total",0),
                                    f"Score ({all_d[-1]})":s2.get("total",0), "Δ":delta,
                                    "Direction":"▲ Improved" if delta>0 else ("▼ Declined" if delta<0 else "→ Same")})
                st.dataframe(pd.DataFrame(chg).sort_values("Δ", ascending=False), use_container_width=True)

# ══════ COMPARE ══════════════════════════════════════════════════════════════
elif page == "⚖️ Compare":
    c1,c2 = st.columns(2)
    sa_name = c1.selectbox("State/UT A", sorted(scores.keys()), index=0)
    sb_name = c2.selectbox("State/UT B", sorted(scores.keys()), index=1)
    if sa_name == sb_name:
        st.warning("Select two different States/UTs.")
    else:
        sa, sb = scores[sa_name], scores[sb_name]
        def gv_all(s):
            return {"ra":gv(s,"ra","resource_adequacy"),"fv":gv(s,"fv","financial_viability"),
                    "el":gv(s,"el","ease_of_living"),"et":gv(s,"et","energy_transition"),
                    "rg":gv(s,"rg","regulatory_governance"),"total":s.get("total",0),"grade":s.get("grade","E")}
        va, vb = gv_all(sa), gv_all(sb)
        col1, col2 = st.columns(2)
        for col, name, v in [(col1,sa_name,va),(col2,sb_name,vb)]:
            with col:
                g = v["grade"]
                st.markdown(f"""
                <div style="text-align:center;background:#f8f9fa;border-radius:10px;padding:1.2rem;border:1px solid #ddd">
                  <b style="font-size:1.1rem">{name}</b><br>
                  {grade_pill(g)}<br>
                  <span style="font-size:2.5rem;font-weight:800;color:{GRADE_COLOR[g]}">{v['total']}</span>
                  <span style="color:#888"> / 100</span>
                </div>""", unsafe_allow_html=True)
        st.markdown("---")
        cmp_rows = []
        for label, key, mx in [("Resource Adequacy","ra",32),("Financial Viability","fv",25),
                                ("Ease of Living","el",23),("Energy Transition","et",15),
                                ("Regulatory Governance","rg",5),("**Total**","total",100)]:
            av, bv = va[key], vb[key]
            win = f"✅ {sa_name}" if av>bv else (f"✅ {sb_name}" if bv>av else "Tied")
            cmp_rows.append({"Parameter":label, sa_name:f"{av}/{mx}", sb_name:f"{bv}/{mx}", "Better":win})
        st.table(pd.DataFrame(cmp_rows))
        st.markdown("#### Parameter Comparison (%)")
        chart_data = pd.DataFrame({
            sa_name:[va["ra"]/32*100,va["fv"]/25*100,va["el"]/23*100,va["et"]/15*100,va["rg"]/5*100],
            sb_name:[vb["ra"]/32*100,vb["fv"]/25*100,vb["el"]/23*100,vb["et"]/15*100,vb["rg"]/5*100],
        }, index=["Res. Adequacy","Fin. Viability","Ease of Living","Energy Trans.","Reg. Governance"])
        st.bar_chart(chart_data)

# ══════ HISTORY ══════════════════════════════════════════════════════════════
elif page == "📋 History":
    rows_h = []
    for d, snap in sorted(data["assessments"].items(), reverse=True):
        sc  = snap["scores"]
        avg = round(sum(v.get("total",0) for v in sc.values())/max(len(sc),1), 2)
        rows_h.append({"Date":d,"Label":snap["label"],"States":len(sc),"Avg Score":avg,
                       "Notes":snap.get("notes","")[:60]})
    st.dataframe(pd.DataFrame(rows_h), use_container_width=True)
    if data["audit_log"]:
        st.markdown("#### Audit Log")
        st.dataframe(pd.DataFrame(data["audit_log"]), use_container_width=True)
    st.markdown("---")
    deletable = [d for d in sorted(data["assessments"].keys()) if d != "2025-03-31"]
    if deletable:
        del_sel = st.selectbox("Delete an assessment (baseline protected)", deletable)
        if st.button("🗑️ Delete", type="secondary"):
            del data["assessments"][del_sel]
            save_data(data)
            st.success(f"Deleted {del_sel}")
            st.rerun()
    else:
        st.info("Only the baseline exists. Add new assessments to manage them here.")

st.markdown("---")
st.caption("First Report: Rating Regulatory Performance of States & UTs | Power Foundation of India & REC Ltd. | Ministry of Power, GoI")
