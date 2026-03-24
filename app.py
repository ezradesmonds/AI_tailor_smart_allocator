import streamlit as st
import pandas as pd
import os
import time

# IMPORT LOGIKA DARI FILE ALLOCATION.PY
# Pastikan file allocation.py ada di folder yang sama
from allocation import hitung_rekomendasi 

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(
    page_title="Sistem Alokasi Penjahit KSMB",
    page_icon="🧵",
    layout="wide"
)

# Custom CSS untuk mempercantik tampilan
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        font-weight: bold;
    }
    .metric-card {
        background-color: white;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. LOAD DATA (Hanya Membaca CSV)
# ==========================================
file_path = 'DATA_FINAL_CLUSTERED.csv'

if not os.path.exists(file_path):
    st.error("⚠️ File 'DATA_FINAL_CLUSTERED.csv' tidak ditemukan!")
    st.warning("👉 Jalankan dulu: python feature_engineering.py")
    st.stop()

# Load data
df = pd.read_csv(file_path)

# ==========================================
# 3. SIDEBAR (INPUT PROJECT)
# ==========================================
with st.sidebar:
    st.header("📝 Input Project Baru")
    st.markdown("Masukkan detail pesanan yang masuk ke Koperasi.")
    st.divider()
    
    nama_project = st.text_input("Nama Project", placeholder="Contoh: Seragam SD Al-Azhar")
    
    # Opsi harus SAMA PERSIS dengan keys di allocation.py
    jenis_project = st.selectbox(
        "Jenis Kategori Project",
        ["Umum", "Seragam Sekolah", "Seragam Pramuka", "Rok Seragam", "Kemeja/Batik", "Custom/Gamis/Sulit"]
    )
    
    col_a, col_b = st.columns(2)
    with col_a:
        jumlah_pcs = st.number_input("Jml Pcs", min_value=1, value=50, step=10)
    with col_b:
        # Kalkulasi estimasi hari (opsional, visual saja)
        est_hari = st.number_input("Target Hari", min_value=1, value=7)
        
    deadline_status = st.radio(
        "Kondisi Deadline",
        ["Santai (Normal)", "Urgent (Buru-buru!)"],
        index=0
    )
    
    st.markdown("---")
    tombol_cari = st.button("🔍 CARI PENJAHIT TERBAIK")

# ==========================================
# 4. HALAMAN UTAMA (DASHBOARD)
# ==========================================

# Judul
st.title("🧵 Smart Tailor Allocation System")
st.markdown("**Koperasi Sumber Mulia Barokah** - *Decision Support System*")
st.divider()

# Tampilkan Statistik Sekilas (Hanya muncul jika belum klik cari)
if not tombol_cari:
    st.subheader("📊 Statistik Penjahit Saat Ini")
    
    # Menghitung jumlah per kategori
    total_penjahit = len(df)
    total_elite = len(df[df['Kategori_ML'].str.contains('Elite')])
    total_standar = len(df[df['Kategori_ML'].str.contains('Standar')])
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Mitra Penjahit", f"{total_penjahit} Orang")
    c2.metric("Tim Elite (Cepat)", f"{total_elite} Orang")
    c3.metric("Tim Standar (Rapi)", f"{total_standar} Orang")
    
    # Visualisasi Peta Sebaran (Scatter Plot)
    st.markdown("### 📍 Peta Sebaran Kinerja Penjahit")
    st.scatter_chart(
        df,
        x='Usia',
        y='Jarak Rumah ke Koperasi (Km)',
        color='Kategori_ML',
        size=100,
        height=400
    )
    st.info("💡 Grafik di atas adalah hasil Machine Learning (Clustering) yang memetakan karakter penjahit.")

# ==========================================
# 5. HASIL REKOMENDASI
# ==========================================
else:
    # Loading animation biar keren
    with st.spinner('🤖 AI sedang menganalisis kecocokan penjahit...'):
        time.sleep(1) # Simulasi loading sebentar
        
        # --- PANGGIL FUNGSI OTAK (ALLOCATION.PY) ---
        hasil_df, pesan_strategi = hitung_rekomendasi(
            df_input=df,
            jenis_project=jenis_project,
            jumlah_pcs=jumlah_pcs,
            kondisi_deadline=deadline_status
        )
        # -------------------------------------------
    
    st.subheader(f"✅ Rekomendasi untuk: {nama_project}")
    
    # Tampilkan Pesan Strategi (Kotak Berwarna)
    if "Urgent" in deadline_status:
        st.error(pesan_strategi) # Merah
    else:
        st.success(pesan_strategi) # Hijau
        
    # Tampilkan Tabel Hasil
    st.markdown("### 🏆 Top 10 Penjahit Paling Cocok")
    
    # Format tabel agar angka desimalnya rapi
    st.dataframe(
        hasil_df.style.format({
            "FINAL_SCORE": "{:.2f}",
            "Est. Speed (Pcs/Hari)": "{:.1f}",
            "Jarak (Km)": "{:.1f}",
            "Kerapian": "{:.0f}"
        }).background_gradient(subset=['FINAL_SCORE'], cmap="Greens"),
        use_container_width=True,
        height=500
    )
    
    # Tombol Reset
    if st.button("⬅️ Kembali ke Dashboard"):
        st.rerun()