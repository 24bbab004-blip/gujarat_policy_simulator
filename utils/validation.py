import pandas as pd
REQUIRED = {"district", "population", "households", "development_index", "capacity_index"}
def validate_dataset(df, valid_districts):
    findings = []
    missing = REQUIRED - set(df.columns)
    if missing: findings.append(f"Missing required columns: {', '.join(sorted(missing))}")
    if not missing:
        if df.isna().any().any(): findings.append(f"Missing values: {int(df.isna().sum().sum())}")
        if df.duplicated().any(): findings.append(f"Duplicate rows: {int(df.duplicated().sum())}")
        invalid = set(df.district.dropna()) - set(valid_districts)
        if invalid: findings.append(f"Invalid district names: {', '.join(sorted(invalid))}")
        numeric = ["population", "households", "development_index", "capacity_index"]
        for col in numeric:
            values = pd.to_numeric(df[col], errors="coerce")
            if values.isna().any(): findings.append(f"Incorrect data type in {col}")
            if (values < 0).any(): findings.append(f"Negative values in {col}")
    return findings
