# Margin Notes — Retail Market Intelligence & Client Proposal Analytics

A beginner-friendly analytics portfolio project built around the Kaggle Superstore dataset. It combines data cleaning, exploratory analysis, business KPIs, a dashboard, and a practical reporting angle for client proposals.

## What it does

- Loads a small included demo dataset so the app runs immediately.
- Accepts a Superstore-style CSV upload.
- Calculates sales, profit, profit margin, orders, customers, units, and average discount.
- Visualizes trends and category profitability.
- Highlights sub-categories for further investigation.
- Uses transparent language: a pattern is a lead to investigate, not proof of cause.

## 1. Download the Kaggle dataset

Download the CSV from:
https://www.kaggle.com/datasets/vivek468/superstore-dataset-final

Extract the archive if necessary. The app accepts a CSV with at least `Sales` and `Profit`. Date, category, region, sub-category, discount, quantity, customer name, and order ID fields add more analysis.

## 2. Set up the project

Install Python 3.10 or newer. Open a terminal in this folder.

### Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, you can run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## 3. Load the Kaggle CSV

Use **Choose Superstore CSV**, select the downloaded CSV, and click **Refresh dashboard**. Your uploaded file is stored locally under `uploads/current.csv`. Click **Reset demo data** to return to the included example.

The sample file is synthetic demo data and is clearly intended only to test the interface. Replace it with the Kaggle dataset for your actual analysis.

## 4. Suggested analysis questions

1. Which product sub-categories have the lowest total profit?
2. Are there categories where sales are high but profit is weak?
3. How do sales and profit change by month?
4. Which regions and customer segments contribute most to profit?
5. What happens to profit in rows with larger discounts? Treat this as a pattern to investigate; do not claim discount caused a loss without further analysis.
6. Which recommendations could be tested in a small pilot?

## 5. Business deliverables for your portfolio

Include these in your final GitHub repository:
- Dashboard screenshots.
- A short EDA notebook or analysis script.
- A 1–2 page executive summary with charts.
- A recommendation table containing issue, evidence, action, KPI, and caveat.
- A short executive summary with charts.

## Project structure

```text
superstore_client_intelligence/
├── app.py
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── dashboard.js
├── data/
│   └── sample_superstore.csv
└── powerbi/
    ├── powerbi_build_guide.md
    ├── measures.dax
    └── margin_notes_theme.json
```

## Notes

- This is a portfolio/demo application, not a production service.
- The secret key in `app.py` is for local development only.
- Do not upload confidential client data.
- Figures will differ based on the dataset file you load.
