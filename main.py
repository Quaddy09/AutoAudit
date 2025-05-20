import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ──────────────────────────────────────────────────
st.set_page_config(page_title="AutoAudit – ISO27001 SOA", layout="wide")
st.title("🛡️ AutoAudit – ISO 27001 Service Orientation Audit")
st.markdown("""
Upload your **(SOA) ISO 27K-22** sheet and instantly see:
- ✅ Controls with observations  
- ⚠️ Risk levels based on gaps  
- 📊 Compliance percentages  
- 💡 A targeted improvement list  
""")

# ──────────────────────────────────────────────────
# Password (optional)
PASSWORD = st.secrets.get("PASSWORD", "secureaudit")
if st.text_input("🔒 Enter password:", type="password") != PASSWORD:
    st.warning("🔑 Incorrect password.")
    st.stop()

# ──────────────────────────────────────────────────
# Load & Reformat
uploaded = st.file_uploader("📂 Upload SOA Excel (.xlsx)", type="xlsx")
if uploaded:
    # Use row 3 (zero‑indexed 2) as header
    df_raw = pd.read_excel(uploaded, header=2)
    # Extract and rename key columns
    df = df_raw.rename(columns={
        'Referensi Kebijakan': 'Clause/Annex',
        'Unnamed: 3': 'Control Name',
        'Gap Assessment': 'Status Observation'
    })[['Clause/Annex', 'Control Name', 'Status Observation']]
    # Drop empty rows
    df = df.dropna(subset=['Clause/Annex', 'Control Name'], how='all')
    
    # ──────────────────────────────────────────────────
    # Map Status → Risk
    def infer_risk(text):
        t = str(text).lower()
        if 'tidak' in t or 'no' in t or t.strip() == '':
            return ('Not Implemented', 3, 'High')
        if 'sebagian' in t or 'partial' in t:
            return ('Partially Implemented', 2, 'Medium')
        return ('Implemented', 1, 'Low')
    
    df[['Status English','Risk Score','Risk Level']] = df['Status Observation'] \
        .apply(infer_risk).tolist()

    # ──────────────────────────────────────────────────
    # Metrics
    total = len(df)
    counts = df['Risk Level'].value_counts().reindex(['Low','Medium','High'], fill_value=0)
    pct = (counts / total * 100).round(1)

    st.markdown("### 🔢 Compliance Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("✅ Low Risk", f"{counts['Low']} / {total}", f"{pct['Low']}%")
    c2.metric("⚠️ Medium Risk", f"{counts['Medium']} / {total}", f"{pct['Medium']}%")
    c3.metric("❌ High Risk", f"{counts['High']} / {total}", f"{pct['High']}%")

    # ──────────────────────────────────────────────────
    # Detailed Table
    st.subheader("📋 Detailed Controls")
    st.dataframe(df, use_container_width=True)

    # CSV export
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "soa_analysis.csv", "text/csv")

    # Improvement suggestions
    lacking = df[df['Risk Level']=='High']
    st.subheader("💡 Improvement Plan")
    if lacking.empty:
        st.success("All controls are implemented or partially implemented.")
    else:
        st.write(f"**{len(lacking)}** high‑risk controls to prioritize:")
        for _, r in lacking.iterrows():
            st.write(f"- **{r['Clause/Annex']}**: {r['Control Name']}")

    # PDF export
    def make_pdf(df):
        buf = BytesIO()
        pdf = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 40
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30, y, "AutoAudit – SOA ISO 27001 Gap Analysis")
        pdf.setFont("Helvetica", 10)
        y -= 30
        pdf.drawString(30, y, f"Low Risk: {counts['Low']} ({pct['Low']}%)")
        pdf.drawString(200, y, f"Medium Risk: {counts['Medium']} ({pct['Medium']}%)")
        pdf.drawString(430, y, f"High Risk: {counts['High']} ({pct['High']}%)")
        y -= 30
        if not lacking.empty:
            pdf.drawString(30, y, "High-Risk Controls:")
            y -= 15
            for _, r in lacking.iterrows():
                pdf.drawString(40, y, f"{r['Clause/Annex']} – {r['Control Name']}")
                y -= 12
                if y < 40:
                    pdf.showPage(); y = h - 40
        pdf.save()
        buf.seek(0)
        return buf

    pdf_buf = make_pdf(df)
    st.download_button("📄 Download PDF Report", pdf_buf, "soa_gap_report.pdf", "application/pdf")

else:
    st.info("🔍 Awaiting your SOA Excel upload…")
