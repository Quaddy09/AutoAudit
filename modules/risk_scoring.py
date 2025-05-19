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

def get_risk_level(score):
    if score == 1:
        return "Low"
    elif score == 2:
        return "Medium"
    elif score == 3:
        return "High"
    return "Unknown"

def assign_risk_scores(df):
    df["Risk Score"] = df.apply(calculate_risk, axis=1)
    df["Risk Level"] = df["Risk Score"].apply(get_risk_level)
    return df

