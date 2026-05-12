# Tech Value Dashboard

A simple Streamlit dashboard for ranking top technology companies by undervaluation metrics.

## Setup

1. Create and activate a Python environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run

```bash
streamlit run app.py
```

## What it does

- Fetches financial metrics for a universe of Fortune 500 companies using `yfinance`
- Computes valuation ratios like P/E, P/B, PEG, and FCF yield
- Creates a composite undervaluation score to rank companies
- Filters by subsector and shows selected company details
- Displays a 1-year price history chart and trading volume for the selected ticker
- Supports both Fortune 500 tech companies and a broader Top Fortune 500 company universe
