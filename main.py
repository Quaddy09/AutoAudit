import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ──────────────────────────────────────────────────
# App Title and Description
# ──────────────────────────────────────────────────
st.set_page_config(page_title="AutoAudit - IT Risk Audit Tool", layout="wide")
st.title("🛡️ AutoAudit – IT Audit Automation Toolkit")
st.markdown("""
Welcome to **AutoAudit**, a smart tool to help IT departments streamline internal audits.  
Upload an Excel file using our [audit template](https://github.com/YOUR_USERNAME/AutoAudit/blob/main/sample-audit-template.xlsx) and get instant risk insights.

**Features:**
- Maps control status to risk scores  
- Displays risk levels: Low / Medium / High  
- Exports results to CSV & PDF  
- Simple password protection  
""")

# ──────────────────────────────────────────────────
# Basic Authentication
# ──────────────────────────────────────────────────
PASSWORD = "secureaudit"
if st.text_input("🔒 Enter password:", type="password") != PASSWORD:
    st.warning("🔑 Incorrect password.")
    st.stop()

# ──────────────────────────────────────────────────
# File Upload and Processing
# ──────────────────────────────────────────────────
uploaded_file = st.file_uploader("📂 Upload Audit Excel (.xlsx)", type="xlsx")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    required = ['Control Domain', 'Control Name', 'Implementation Status']
    if not all(col in df.columns for col in required):
        st.error(f"Missing columns: {', '.join(required)}")
        st.stop()

    # Map status → score/level
    status_map = {"Implemented": 1, "Partially Implemented": 2, "Not Implemented": 3}
    level_map  = {1: "Low", 2: "Medium", 3: "High"}
    df['Risk Score'] = df['Implementation Status'].map(status_map)
    df['Risk Level'] = df['Risk Score'].map(level_map)

    st.success("✅ Processed successfully!")
    st.subheader("📊 Audit Results")
    st.dataframe(df, use_container_width=True)

    # Download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "AutoAudit_Report.csv", "text/csv")

    # Download PDF
    def make_pdf(df):
        buf = BytesIO()
        pdf = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 30
        pdf.setFont("Helvetica-Bold", 12)
        pdf.drawString(30, y, "AutoAudit – Risk Audit Summary")
        pdf.setFont("Helvetica", 10)
        y -= 20
        for _, row in df.iterrows():
            line = (f"{row['Control Domain']} | {row['Control Name']} | "
                    f"Status: {row['Implementation Status']} → {row['Risk Level']}")
            pdf.drawString(30, y, line)
            y -= 15
            if y < 40:
                pdf.showPage(); y = h - 30
        pdf.save()
        buf.seek(0)
        return buf

    pdf_buf = make_pdf(df)
    st.download_button("📄 Download PDF", pdf_buf, "AutoAudit_Summary.pdf", "application/pdf")

else:
    st.info("🔍 Awaiting your upload…")
