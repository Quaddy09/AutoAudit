import streamlit as st
import pandas as pd

# Judul Aplikasi
st.set_page_config(page_title="Audit ISO 27001 - AutoAudit", layout="wide")
st.title("Audit ISO 27001 - AutoAudit")

# Upload file Excel
uploaded_file = st.file_uploader("Unggah file Excel Kertas Kerja ICT:", type=["xlsx"])

if uploaded_file:
    try:
        sheet_name = "Kertas Kerja ICT"
        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=5)

        # Ambil kolom yang relevan
        df = df.iloc[:, [2, 3, 6, 7, 8, 9]]
        df.columns = [
            "No",
            "Klausa/Annex",
            "Fungsi",
            "Pedoman",
            "TKO/TKI",
            "Hasil Observasi"
        ]

        # Bersihkan data kosong
        df = df[df["Klausa/Annex"].notna()]

        # Interpretasi status implementasi
        def interpret_status(text):
            text = str(text).lower()
            if "belum" in text or "tidak ada" in text:
                return "Belum Implementasi"
            elif "dalam" in text or "proses" in text:
                return "Dalam Proses"
            elif "sudah" in text or "tersedia" in text:
                return "Sudah Implementasi"
            else:
                return "Tidak Diketahui"

        df["Status Implementasi"] = df["Hasil Observasi"].apply(interpret_status)

        # Tambahkan kolom skor risiko dummy (bisa diisi manual nanti)
        df["Skor Risiko"] = "-"

        # Tambahkan kolom prioritas dummy
        df["Prioritas"] = df["Status Implementasi"].apply(
            lambda x: "Tinggi" if x == "Belum Implementasi" else "Sedang" if x == "Dalam Proses" else "Rendah")

        # Tampilkan hasil
        st.success("Berhasil membaca dan menganalisis dokumen audit.")
        st.dataframe(df, use_container_width=True)

        # Ringkasan status implementasi
        st.subheader("📊 Ringkasan Status Implementasi")
        status_counts = df["Status Implementasi"].value_counts()
        st.write(status_counts)

        st.subheader("⚠️ Rekomendasi Prioritas")
        for _, row in df[df["Prioritas"] == "Tinggi"].iterrows():
            st.markdown(f"**{row['No']} - Annex {row['Annex']}**: {row['Hasil Observasi']}")

    except Exception as e:
        st.error(f"Gagal memproses file: {e}")
else:
    st.info("Silakan unggah file Excel untuk memulai audit.")
