import streamlit as st
import pandas as pd
from audit_logic import run_audit

st.set_page_config(page_title="AutoAudit", layout="wide")
st.title("\U0001F50D AutoAudit – IT Audit Automation Toolkit")
st.markdown("Upload your audit data and let the system analyze it automatically.")

uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("\U0001F4C8 Input Data Preview")
    st.dataframe(df)

    if st.button("Run Audit"):
        result = run_audit(df)
        st.subheader("\u2705 Audit Results")
        st.dataframe(result)