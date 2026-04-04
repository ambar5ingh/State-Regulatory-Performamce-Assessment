# ⚡ Regulatory Performance Rating – States & Union Territories

A Streamlit-based dashboard to assess and monitor the regulatory performance of all Indian States and Union Territories over time, based on the **First Report: Rating Regulatory Performance of States and UTs** by Power Foundation of India (PFI) & REC Ltd., Ministry of Power, Government of India.

---

## 📋 Features

| Page | Description |
|---|---|
| 📊 Dashboard & Rankings | National overview, KPIs, rankings table, score distribution bar/pie charts, parameter heatmap |
| 🔍 State/UT Profile | Detailed scorecard with gauge, radar chart, progress bars, and historical trend |
| 📝 New Assessment Entry | Enter scores for a new assessment cycle (periodic update) |
| 📈 Trend Analysis | Multi-period trend lines by state/UT and parameter |
| ⚖️ Compare States/UTs | Side-by-side radar + table comparison of any two entities |
| 📋 Assessment History | Full audit log and management of saved assessments |

---

## 🏗️ Assessment Framework (from the Report)

### Parameters & Max Marks
| # | Parameter | Max Marks | Weight |
|---|---|---|---|
| 1 | Resource Adequacy (Reliable Power Supply) | 32 | 32% |
| 2 | Financial Viability of DISCOMs | 25 | 25% |
| 3 | Ease of Living / Doing Business | 23 | 23% |
| 4 | Energy Transition | 15 | 15% |
| 5 | Regulatory Governance | 5 | 5% |
| | **Total** | **100** | **100%** |

### Grading Criteria
| Grade | Score Range |
|---|---|
| A | ≥ 85 marks |
| B | 65 – 84 marks |
| C | 50 – 64 marks |
| D | 35 – 49 marks |
| E | < 35 marks |

---

## 🚀 How to Run

```bash
# Install dependencies
pip install -r requirements.txt

# Launch the app
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

---

## 🔄 Periodic Assessment Workflow

1. Open the app → go to **"📝 New Assessment Entry"**
2. Enter the assessment date and a label (e.g., "ARR FY 2026-27 / True-up FY 2024-25")
3. Expand each state and enter updated sub-parameter scores
4. Click **"Save Assessment"** – scores are persisted in `assessment_data.json`
5. All pages (trends, profiles, comparisons) update automatically

---

## 📁 Files

```
regulatory_performance_app/
├── app.py                  # Main Streamlit application
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── assessment_data.json    # Auto-generated; stores all assessment data
```

---

## 📖 Data Source

- **Report**: First Report: Rating Regulatory Performance of States and Union Territories
- **Published by**: Power Foundation of India (PFI) & REC Ltd.
- **Under**: Ministry of Power, Government of India
- **Assessment cut-off**: 31 March 2025 (extended: 30 June 2025)
- **Legal basis**: Electricity Act 2003, MoP Rules, APTEL Judgments, Tariff Policy 2016
