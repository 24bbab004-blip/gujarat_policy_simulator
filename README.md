# Gujarat Policy Simulator

Local decision-support prototype for exploring the **estimated** cost, reach, impact, risk and efficiency of Gujarat policy scenarios. It is not an official Government of Gujarat product and all bundled data is synthetic demo data.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

The app creates `policy_simulator.db` automatically. No passwords, API keys, or external services are needed.

## Included features

- Seven policy categories and a guided simulation workflow
- Gujarat-wide or multi-district modelling for all 33 current districts
- Transparent financial, impact, risk, efficiency, sensitivity and uncertainty calculations
- SQLite scenario library, comparison charts, data upload validation and PDF reports
- Synthetic district demo data and four instant demo scenarios

## Replacing demo data

Replace `data/districts.csv` with a CSV containing `district`, `population`, `households`, `development_index`, and `capacity_index`. District names must match the selector. The app flags all bundled inputs as synthetic; retain source/year metadata when introducing real public data and validate it through the Data Sources page before policy use.

## Model boundaries

Financial results are arithmetic estimates. Impact results are explainable proxy indicators, not validated causal forecasts. Uncertainty intervals are scenario ranges derived by repeatedly varying specified assumptions, not official confidence intervals. Review results with legal, financial, departmental and domain experts before action.
