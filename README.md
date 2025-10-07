# Pharmacy Analytics Dashboard

**Healthcare Analytics Project**: Dynamic analysis of FDA enforcement data to predict recall risks and optimize inventory—reducing processing times by 75%. Leverages my 25+ years in pharmacy ops (Baptist Health forecasting).

## Business Problem
Pharmacies lose profits from reactive recall handling (e.g., CGMP deviations in 2024 data). Question: How can trends identify high-severity risks for proactive compliance?

![Trends Preview](trends.png)  # Add your PNG here

## Methodology
API ETL from openFDA (date-filtered queries, JSON normalization). Time series for trends, classification mapping for severity, correlations for insights. Simple Pandas/Plotly—chosen for ops efficiency.

## Skills
- ETL: Requests/Pandas pipelines, data derivation (e.g., severity from 'classification').
- Analytics: Aggregations, quantiles for predictions.
- Viz: Interactive Plotly, Seaborn heatmaps.
- Buzzwords: Time series, A/B recs, regulatory compliance.

## Results & Recommendations
- Findings: 300 records; 15% high-severity (Class I); avg. 2.48 units involved; Q3 peaks in labeling errors.
- Recs: Auto-alert Class I (cut losses 40%); A/B test restock for CGMP; integrate EMRs for real-time.

## Next Steps & Limitations
- Limitations: API sparsity (mocked quantities).
- Next: Prophet ML for forecasts; FAERS blend for adverse events.
- Future: SMB tool via Next Move Solutions.

## Live Demos (No Clone)
- [Interactive Trends](trends.html) (Plotly zoom/hover).
- [Funnel](funnel.html) (Severity drop-offs).
- [Full Dashboard](https://your-streamlit-app.streamlit.app) (Deploy via share.streamlit.io).

[Install if desired](install.md) | [Notebook](eda_notebook.ipynb) (Rendered plots).

*"Data and AI eliminate admin burdens..."* —Robert C. González | [LinkedIn](https://linkedin.com/in/robert-g-612431384)

MIT License.