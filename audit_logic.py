def run_audit(df):
    # Dummy logic: add a new column "risk_score"
    df["risk_score"] = 100  # Replace with actual logic or ML model
    return df


# 3. utils.py (Optional helper functions)

def calculate_risk_score(row):
    # Placeholder logic based on column values
    score = 0
    if "control" in row and row["control"] == "missing":
        score += 50
    if "incident" in row and row["incident"] == "yes":
        score += 50
    return score