# main.py

import streamlit as st
from modules.audit_checklist import load_controls
from modules.risk_scoring import assign_risk_scores
from modules.report_generator import generate_pdf_report

st.set_page_config(page_title="AutoAudit - IT Audit Automation", layout="wide")

st.title("AutoAudit 🛡️ - IT Audit Automation Toolkit")

uploaded_file = st.file_uploader("Upload your Audit Excel Checklist (.xlsx)", type="xlsx")

if uploaded_file:
    df = load_controls(uploaded_file)
    if isinstance(df, str):
        st.error(df)
    else:
        df_with_scores = assign_risk_scores(df)
        st.subheader("Audit Checklist with Risk Scores")
        st.dataframe(df_with_scores)
        st.download_button(
            "Download CSV",
            df_with_scores.to_csv(index=False).encode("utf-8"),
            file_name="audit_risk_report.csv",
            mime="text/csv"
        )


        if st.button("Generate PDF Report"):
            generate_pdf_report(df_with_scores)
            with open("audit_report.pdf", "rb") as file:
                st.download_button("Download PDF Report", file, file_name="audit_report.pdf")
        low, med, high = (
            df_with_scores["Risk Level"] == "Low").sum(), (
            df_with_scores["Risk Level"] == "Medium").sum(), (
            df_with_scores["Risk Level"] == "High").sum()

        st.markdown("### 📊 Risk Summary")
        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Low Risk", low)
        col2.metric("🟡 Medium Risk", med)
        col3.metric("🔴 High Risk", high)
        st.markdown("### 📈 Risk Distribution")
