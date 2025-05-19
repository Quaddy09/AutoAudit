# modules/audit_checklist.py

import pandas as pd

def load_controls(file_path):
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        return f"Error loading file: {e}"
