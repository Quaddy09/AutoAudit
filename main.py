# AutoAudit ISO 27001 Compliance Web App (Streamlit Version)
# Dibuat oleh: David Krisna
# Tujuan: Membantu audit ISO 27001 dari file Excel menggunakan dashboard interaktif

import pandas as pd
import streamlit as st
import datetime
import plotly.express as px

# ---------------------- Fungsi Membaca dan Validasi File ----------------------
def load_excel(file):
    try:
        df = pd.read_excel(file)
        required_columns = ['No', 'Annex', 'Fungsi', 'Pedoman / TKO', 'Gap Assessment', 'Status', 'Risk']
        if all(col in df.columns for col in required_columns):
            return df
        else:
            st.error("⚠️ Format file tidak sesuai. Pastikan kolom: " + ", ".join(required_columns))
            return None
    except Exception as e:
        st.error(f"Gagal membaca file: {e}")
        return None

# ---------------------- Fungsi Analisa dan Ringkasan ----------------------
def analyze_data(df):
    total_controls = len(df)
    implemented = len(df[df['Status'].str.lower() == 'implemented'])
    not_implemented = total_controls - implemented
    risk_summary = df['Risk'].value_counts()
    return {
        'total_controls': total_controls,
        'implemented': implemented,
        'not_implemented': not_implemented,
        'risk_summary': risk_summary,
        'per_fungsi': df.groupby('Fungsi')['Status'].value_counts().unstack(fill_value=0)
    }

# ---------------------- Layout Streamlit ----------------------
st.set_page_config(page_title="AutoAudit ISO 27001", layout="wide")
st.title("📋 AutoAudit - ISO/IEC 27001:2022 Gap Assessment")
st.markdown("""
Aplikasi ini digunakan untuk membantu tim IT dan auditor dalam melakukan assessment terhadap kepatuhan ISO 27001.
Upload file Excel dengan format kolom: **No, Annex, Fungsi, Pedoman / TKO, Gap Assessment, Status, Risk**
""")

# Sidebar
st.sidebar.header("🔐 Info Pengguna")
st.sidebar.markdown(f"📅 Hari ini: {datetime.date.today().strftime('%d %B %Y')}")

# Upload File
uploaded_file = st.file_uploader("Upload file Excel Audit ISO 27001:", type=["xlsx"])
if uploaded_file:
    df = load_excel(uploaded_file)
    if df is not None:
        st.success("✅ File berhasil dibaca!")

        # Ringkasan Analisa
        st.subheader("📊 Ringkasan Audit")
        result = analyze_data(df)

        col1, col2, col3 = st.columns(3)
        col1.metric("Kontrol Total", result['total_controls'])
        col2.metric("Sudah Diimplementasi", result['implemented'])
        col3.metric("Belum Implementasi", result['not_implemented'])

        st.markdown("### 🔍 Distribusi Risiko")
        st.bar_chart(result['risk_summary'])

        st.markdown("### 👥 Status per Fungsi")
        st.dataframe(result['per_fungsi'])

        # Tabel Detail Audit
        st.markdown("### 📄 Tabel Detail Audit")
        df_sorted = df.sort_values(by=['Risk'], ascending=False)
        st.dataframe(df_sorted, use_container_width=True)

        # High Risk Prioritas
        st.markdown("### 🚨 Prioritas Tindakan untuk Risiko Tinggi")
        high_risk = df[df['Risk'].str.lower() == 'high']
        if not high_risk.empty:
            for index, row in high_risk.iterrows():
                st.warning(f"**Kontrol {row['No']} - Annex {row['Annex']} ({row['Fungsi']}):** {row['Gap Assessment']}\n\n➡️ Status: {row['Status']} | 📌 Prioritaskan tindakan mitigasi.")
        else:
            st.success("🎉 Tidak ada kontrol dengan risiko tinggi.")

        # Export ke Excel
        with st.expander("⬇️ Download Laporan dalam Excel"):
            from io import BytesIO
            output = BytesIO()
            df.to_excel(output, index=False, sheet_name='Audit Report')
            st.download_button("Download Audit Report", data=output.getvalue(), file_name="audit_report.xlsx")

    else:
        st.stop()
else:
    st.info("📁 Silakan unggah file Excel terlebih dahulu.")