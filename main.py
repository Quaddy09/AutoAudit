import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

st.set_page_config(page_title="AutoAudit – IT Audit Web", layout="wide")
st.title("🛡️ AutoAudit – IT Audit Automation Toolkit")
st.markdown("""
Upload your **PDSI IT audit sheet** and get an instant risk‑scored report.  
This version will automatically detect and rename your columns (no more missing‑column errors).
""")

# Optional password protection
PASSWORD = st.secrets.get("PASSWORD", "secureaudit")
if st.text_input("🔒 Enter password:", type="password") != PASSWORD:
    st.warning("🔑 Incorrect password.")
    st.stop()

def find_header_row(df):
    """Return first row index containing 'Control Name'."""
    return df.apply(lambda r: r.astype(str).str.contains('Control Name', case=False, na=False).any(), axis=1).idxmax()

def fuzzy_map_columns(df):
    """Find columns by keyword and map to our standardized English names."""
    col_map = {}
    for col in df.columns:
        lc = str(col).lower()
        if 'klausa' in lc or 'annex' in lc:
            col_map[col] = 'Clause/Annex'
        elif 'control name' in lc:
            col_map[col] = 'Control Name'
        elif 'persyaratan' in lc or 'description' in lc:
            col_map[col] = 'Control Description'
        elif 'pertanyaan' in lc or 'question' in lc:
            col_map[col] = 'Audit Question'
        elif 'fungsi' in lc or 'function' in lc:
            col_map[col] = 'Responsible Function'
        elif 'observasi' in lc or 'hasil' in lc or 'status' in lc:
            col_map[col] = 'Status Observation'
    return col_map

def load_and_prepare(uploaded_file):
    # 1. Read raw without headers
    raw = pd.read_excel(uploaded_file, header=None)
    hdr_idx = find_header_row(raw)
    df = pd.read_excel(uploaded_file, header=hdr_idx)

    # 2. Fuzzy‑map & rename
    mapping = fuzzy_map_columns(df)
    df = df.rename(columns=mapping)

    # 3. Keep only mapped columns
    keep = list(mapping.values())
    df = df[keep].dropna(how='all')  # drop any all‑empty rows

    # 4. Status → (English, score, level)
    status_map = {
        'belum':   ('Not Implemented',      3, 'High'),
        'sebagian':('Partially Implemented',2, 'Medium'),
        'sudah':   ('Implemented',          1, 'Low'),
    }
    def map_status(s):
        s_str = str(s).lower()
        for key, val in status_map.items():
            if key in s_str:
                return val
        return ('Unknown', 0, 'Unknown')

    df[['Status English','Risk Score','Risk Level']] = df['Status Observation'] \
        .apply(map_status).tolist()

    return df

uploaded = st.file_uploader("📂 Upload your PDSI IT audit sheet (.xlsx)", type="xlsx")
if uploaded:
    try:
        df = load_and_prepare(uploaded)
    except Exception as e:
        st.error(f"❌ Failed to parse sheet: {e}")
        st.stop()

    st.success("✅ File parsed and scored!")
    st.subheader("📊 Audit Results")
    st.dataframe(df, use_container_width=True)

    # CSV download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download CSV", csv, "AutoAudit_Report.csv", "text/csv")

    # PDF download
    def make_pdf(buf_df):
        buf = BytesIO()
        pdf = canvas.Canvas(buf, pagesize=letter)
        w, h = letter
        y = h - 40
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(30, y, "AutoAudit – IT Audit Report")
        pdf.setFont("Helvetica", 10)
        y -= 30
        for _, r in buf_df.iterrows():
            line = (f"{r.get('Clause/Annex','')} | {r.get('Control Name','')} | "
                    f"{r.get('Status English','')} → {r.get('Risk Level','')}")
            pdf.drawString(30, y, line)
            y -= 15
            if y < 40:
                pdf.showPage(); y = h - 40
        pdf.save()
        buf.seek(0)
        return buf

    pdf_buf = make_pdf(df)
    st.download_button("📄 Download PDF", pdf_buf, "AutoAudit_Summary.pdf", "application/pdf")

else:
    st.info("🔍 Awaiting your PDSI IT audit sheet upload…")
