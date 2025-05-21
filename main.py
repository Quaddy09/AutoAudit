import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

# ──────────────────────────────────────────────────
st.set_page_config(page_title="AutoAudit – IT Audit Web", layout="wide")
st.title("🛡️ AutoAudit – IT Audit Automation Toolkit")
st.markdown("""
Upload your **PDSI IT audit sheet** and get an instant risk‑scored report.  
_No need to reformat your Excel — the app will find and rename the proper columns for you!_
""")

# ──────────────────────────────────────────────────
# Simple password (optional)
PASSWORD = "secureaudit"
if st.text_input("🔒 Enter password:", type="password") != PASSWORD:
    st.warning("🔑 Incorrect password.")
    st.stop()

# ──────────────────────────────────────────────────
def load_and_prepare(df_raw):
    # 1. Find the header row (first row containing “Control Name”)
    header_idx = df_raw.apply(lambda r: r.astype(str).str.contains('Control Name').any(), axis=1).idxmax()
    df = pd.read_excel(uploaded_file, header=header_idx)

    # 2. Rename Bahasa‑Indonesia columns to English
    col_map = {
        'Klausa/Annex':          'Clause/Annex',
        'Control Name':          'Control Name',
        'Persyaratan 27001:2022':'Control Description',
        'Pertanyaan':            'Audit Question',
        'Fungsi':                'Responsible Function',
        'Hasil Observasi':       'Status Observation'
    }
    found = {k:v for k,v in col_map.items() if k in df.columns}
    df = df.rename(columns=found)

    # 3. Keep only the ones we need
    keep = list(found.values())
    df = df[keep].dropna(how='all')

    # 4. Map Indonesian status → English + score + level
    status_map = {
        'Belum Dilakukan':        ('Not Implemented',      3, 'High'),
        'Dilakukan Sebagian':      ('Partially Implemented',2, 'Medium'),
        'Sudah Dilakukan':         ('Implemented',          1, 'Low')
    }
    df[['Status English','Risk Score','Risk Level']] = (
        df['Status Observation']
        .apply(lambda s: status_map.get(s, ('Unknown',0,'Unknown')))
        .tolist()
    )
    return df

# ──────────────────────────────────────────────────
uploaded_file = st.file_uploader("📂 Upload PDSI IT audit sheet (.xlsx)", type="xlsx")
if uploaded_file:
    # Read the raw sheet without headers
    raw = pd.read_excel(uploaded_file, header=None)
    try:
        df = load_and_prepare(raw)
    except Exception as e:
        st.error(f"Failed to parse sheet: {e}")
        st.stop()

    st.success("✅ File parsed and scored!")
    st.subheader("📊 Audit Results")
    st.dataframe(df, use_container_width=True)

    # CSV download
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
    def make_pdf(buf_df):
        buf = BytesIO()
        pdf = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 40
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30, y, "AutoAudit – SOA ISO 27001 Gap Analysis")
        pdf.setFont("Helvetica", 10)
        y -= 30
        for _, r in buf_df.iterrows():
            line = (f"{r['Clause/Annex']} | {r['Control Name']} | "
                    f"{r['Status English']} → {r['Risk Level']}")
            pdf.drawString(30, y, line)
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
    st.info("🔍 Awaiting your PDSI IT audit sheet upload...")
