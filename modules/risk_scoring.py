# modules/risk_scoring.py

def calculate_risk(row):
    implemented = row["Implemented"].strip().lower()
    if implemented == "yes":
        return 1
    elif implemented == "partial":
        return 2
    elif implemented == "no":
        return 3
    else:
        return 0

def assign_risk_scores(df):
    df["Risk Score"] = df.apply(calculate_risk, axis=1)
    return df
