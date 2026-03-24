# import pandas as pd

# df = pd.read_excel("Data koperasi/RATIO PENJAHIT.xlsx")

# print(df.head())

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

# ==========================================
# 1. PERSIAPAN DATA (DATA PREPARATION)
# ==========================================

# Load data penjahit
df = pd.read_excel('Data koperasi/RATIO PENJAHIT.xlsx')

# Membersihkan data
# Mengisi spesialis kosong dengan 'Umum'
df['Spesialis'] = df['Spesialis'].fillna('Umum')

# Mengubah kolom True/False menjadi angka 1/0
cols_bool = ['Kerapian', 'Ketepatan Waktu', 'Quantity', 'Komitmen']
for col in cols_bool:
    df[col] = df[col].astype(int)

# Membersihkan kolom Jarak (mengubah koma ',' menjadi titik '.' agar bisa dihitung)
# Misal "8,1" menjadi 8.1
df['Jarak Rumah ke Koperasi (Km)'] = df['Jarak Rumah ke Koperasi (Km)'].astype(str).str.replace(',', '.').astype(float)

# ==========================================
# 2. MACHINE LEARNING: CLUSTERING (K-MEANS)
# ==========================================

# Kita akan cluster berdasarkan performa, bukan nama
features = ['Usia', 'Jarak Rumah ke Koperasi (Km)', 'Kerapian', 'Ketepatan Waktu', 'Quantity', 'Komitmen']
X = df[features].copy()

# Normalisasi Data (Agar Usia 60 tahun tidak mendominasi Jarak 5 km)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Melakukan K-Means Clustering (Membagi menjadi 3 Kelompok Karakteristik)
# n_clusters=3 artinya kita minta komputer cari 3 tipe penjahit
kmeans = KMeans(n_clusters=3, random_state=42)
df['Cluster_Label'] = kmeans.fit_predict(X_scaled)

# Menganalisis hasil Cluster untuk memberi Nama Grup secara Otomatis
# Kita lihat rata-rata skor tiap cluster
cluster_summary = df.groupby('Cluster_Label')[features].mean()

# Logika pemberian nama otomatis berdasarkan statistik data:
# Cluster mana yang punya Quantity c& Ketepatan Waktu tertinggi?
best_cluster = cluster_summary['Quantity'].idxmax()
# Cluster mana yang punya Kerapian terendah?
worst_cluster = cluster_summary['Kerapian'].idxmin()

def namai_cluster(cluster_id):
    if cluster_id == best_cluster:
        return "Grup Elite (Cepat & Bisa Banyak)"
    elif cluster_id == worst_cluster:
        return "Grup Perlu Bimbingan (Resiko Tinggi)"
    else:
        return "Grup Standar / Spesialis Kecil"

df['Kategori_ML'] = df['Cluster_Label'].apply(namai_cluster)

print("--- HASIL CLUSTERING MACHINE LEARNING ---")
print(df[['Nama', 'Kategori_ML', 'Spesialis']].head(10))

# ==========================================
# 3. SISTEM REKOMENDASI (ASSIGNMENT)
# ==========================================

# Menghitung Skor Individu untuk Ranking di dalam Cluster
# Skor ini kombinasi dari logic "Weighted Sum" kamu sebelumnya
# Semakin muda (1-usia_norm) semakin tinggi skor kecepatannya
df['Usia_Norm'] = scaler.fit_transform(df[['Usia']])
df['Jarak_Norm'] = scaler.fit_transform(df[['Jarak Rumah ke Koperasi (Km)']])

df['Skor_Kecepatan'] = (
    ((1 - df['Usia_Norm']) * 1.5) +  # Muda = Cepat
    ((1 - df['Jarak_Norm']) * 1.0) + # Dekat = Cepat
    (df['Quantity'] * 2.0) +         # Sanggup banyak
    (df['Ketepatan Waktu'] * 2.0)    # Tepat waktu
)

def cari_penjahit_cerdas(tipe_project, deadline_mepet=False, butuh_seragam=False):
    print(f"\n[MENCARI PENJAHIT] Project: {tipe_project} | Deadline Mepet: {deadline_mepet}")
    
    # 1. Filter Spesialisasi
    calon = df.copy()
    if butuh_seragam:
        calon = calon[calon['Spesialis'].isin(['Semua', 'Seragam'])]
    
    # 2. Filter Berdasarkan Cluster ML
    if deadline_mepet:
        # Jika mepet, HANYA ambil dari grup Elite
        calon = calon[calon['Kategori_ML'] == "Grup Elite (Cepat & Bisa Banyak)"]
        prioritas = 'Skor_Kecepatan'
    else:
        # Jika santai, hindari grup resiko tinggi saja
        calon = calon[calon['Kategori_ML'] != "Grup Perlu Bimbingan (Resiko Tinggi)"]
        prioritas = 'Skor_Kecepatan' # Atau bisa buat Skor_Kerapian terpisah

    # 3. Urutkan Ranking
    hasil = calon.sort_values(by=prioritas, ascending=False)
    
    return hasil[['Nama', 'Kategori_ML', 'Spesialis', 'Jarak Rumah ke Koperasi (Km)', 'Skor_Kecepatan']].head(5)

# ==========================================
# 4. CONTOH PENGGUNAAN
# ==========================================

# Kasus A: Project Seragam Sekolah, Deadline BESOK (Butuh Cepat & Banyak)
rekomendasi_A = cari_penjahit_cerdas("Seragam Sekolah", deadline_mepet=True, butuh_seragam=True)
print("\n--- REKOMENDASI PROJECT CEPAT (SERAGAM) ---")
print(rekomendasi_A)

# Kasus B: Project Santai
rekomendasi_B = cari_penjahit_cerdas("Jahit Biasa", deadline_mepet=False, butuh_seragam=False)
print("\n--- REKOMENDASI PROJECT SANTAI ---")
print(rekomendasi_B)