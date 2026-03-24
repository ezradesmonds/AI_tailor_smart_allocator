# import pandas as pd
# import numpy as np
# from sklearn.preprocessing import MinMaxScaler

# def hitung_rekomendasi(df_input, jenis_project, jumlah_pcs, kondisi_deadline):
#     """
#     Sistem Alokasi Penjahit Cerdas (Logic Based on User Preference)
#     """
#     # 1. SETUP DATA
#     # ---------------------------------------------------------
#     df = df_input.copy()
#     scaler = MinMaxScaler()
    
#     # Mapping Input User ke Kolom Kapabilitas di Excel (History Data)
#     # Tujuannya: Mengecek apakah dia PERNAH mengerjakan jenis ini?
#     map_kapabilitas = {
#         "Seragam Sekolah": ["Seragam Hem Putih (Pcs/hari)", "Seragam Hem Pramuka (Pcs/hari)"],
#         "Seragam Pramuka": ["Seragam Hem Pramuka (Pcs/hari)", "Celana Pramuka Seragam (Pcs/hari)"],
#         "Rok Seragam": ["Rok Seragam (Pcs/hari)"],
#         "Kemeja/Batik": ["Kemeja Kerja (Pcs/hari)"],
#         "Custom/Gamis/Sulit": ["Custom (Sulit) (Pcs/hari)"]
#     }
    
#     # Tentukan kolom kapabilitas yang relevan
#     kolom_kapabilitas = map_kapabilitas.get(jenis_project, [])
    
#     # 2. FILTERING AWAL (Hard Constraints)
#     # ---------------------------------------------------------
#     # Aturan: "Jangan beri penjahit yang tidak pernah mengerjakan pesanan sulit"
#     if jenis_project == "Custom/Gamis/Sulit":
#         # Hapus penjahit yang history Custom-nya 0
#         df = df[df['Custom (Sulit) (Pcs/hari)'] > 0].copy()
#         if df.empty:
#             return df, "⚠️ Tidak ada penjahit yang memiliki history mengerjakan Custom/Sulit!"

#     # 3. PERHITUNGAN SKOR (Feature Engineering on the Fly)
#     # ---------------------------------------------------------
    
#     # --- A. SKOR USIA (Golden Age Logic) ---
#     # User: "Tengah-tengah paling ideal" (sekitar 35-45 tahun).
#     # Rumus: 1 dikurangi selisih jarak dari angka 40.
#     # Hasil: Usia 40 dpt skor 1.0, Usia 20 dpt skor rendah, Usia 60 dpt skor rendah.
#     df['Selisih_Usia'] = abs(df['Usia'] - 40)
#     df['Skor_Usia'] = 1 - scaler.fit_transform(df[['Selisih_Usia']])

#     # --- B. SKOR JARAK vs QUANTITY (Efisiensi) ---
#     # Normalisasi Jarak dulu (0 = Dekat, 1 = Jauh)
#     df['Jarak_Norm'] = scaler.fit_transform(df[['Jarak Rumah ke Koperasi (Km)']])
    
#     # User: "Kalau order banyak, biar dia ga bolak balik (Jauh gpp). Kalau dikit, cari yang dekat."
#     if jumlah_pcs < 20:
#         # ORDER KECIL: Prioritas DEKAT (Jarak kecil = Skor Tinggi)
#         df['Skor_Lokasi'] = 1 - df['Jarak_Norm'] 
#         pesan_jarak = "📦 Order Kecil: Memprioritaskan penjahit TERDEKAT (hemat waktu)."
#     elif jumlah_pcs > 50:
#         # ORDER BESAR: Jauh tidak masalah, malah diprioritaskan agar yg dekat bisa handle yg urgent/kecil
#         # Kita beri skor lebih tinggi sedikit untuk yang agak jauh tapi masih wajar
#         df['Skor_Lokasi'] = df['Jarak_Norm'] * 0.5 + 0.5 # Logic santai
#         pesan_jarak = "🚛 Order Besar: Lokasi Jauh tidak masalah (sekali angkut)."
#     else:
#         # ORDER MENENGAH: Netral
#         df['Skor_Lokasi'] = 0.5 # Flat score

#     # --- C. SKOR PERFORMA DASAR (Kerapian, Komitmen, Tepat Waktu) ---
#     # Ini 1/0, jadi langsung dikali bobot
#     df['Skor_Attitude'] = (
#         (df['Kerapian'] * 30) +         # Paling Penting (Bobot 30%)
#         (df['Komitmen'] * 25) +         # Penting (Bobot 25%)
#         (df['Ketepatan Waktu'] * 20)    # Penting (Bobot 20%)
#     ) 

#     # --- D. SKOR KAPABILITAS (History Kecepatan) ---
#     # Mengambil rata-rata kecepatan mereka di jenis baju yg dipilih
#     if kolom_kapabilitas:
#         # Ambil rata-rata jika ada 2 kolom (misal seragam putih & pramuka)
#         df['Raw_Kapabilitas'] = df[kolom_kapabilitas].mean(axis=1)
#         # Normalisasi (Siapa yg paling ngebut dpt skor 1)
#         df['Skor_Kapabilitas'] = scaler.fit_transform(df[['Raw_Kapabilitas']])
#     else:
#         df['Skor_Kapabilitas'] = 0.5 # Default jika project umum

#     # --- E. SKOR SPESIALIS (Match Making) ---
#     # User: "Prioritas dulu yg spesialis tertentu baru yg smua"
#     def hitung_match_spesialis(row):
#         spesialis = str(row['Spesialis']).lower()
#         project = jenis_project.lower()
        
#         # 1. Perfect Match (Spesifik)
#         if "seragam" in project and "seragam" in spesialis and "semua" not in spesialis:
#             return 1.0 # Nilai Tertinggi
#         # 2. General Match (Bisa Semua)
#         elif "semua" in spesialis:
#             return 0.8 # Nilai Tinggi tapi prioritas kedua
#         # 3. Partial Match (Misal Project Rok, Spesialis Rok)
#         elif "rok" in project and "rok" in spesialis:
#             return 0.9
#         # 4. Basic (Hanya bisa rok/celana tapi disuruh jahit kemeja)
#         else:
#             return 0.2 # Rendah
            
#     df['Skor_Spesialis'] = df.apply(hitung_match_spesialis, axis=1)

#     # 4. FINAL CALCULATION (BOBOT BERDASARKAN DEADLINE)
#     # ---------------------------------------------------------
#     # Di sini kita gabungkan semua skor di atas menjadi satu Final Score
    
#     if kondisi_deadline == "Urgent (Buru-buru!)":
#         # STRATEGI URGENT: Fokus Kecepatan & Kapabilitas
#         df['FINAL_SCORE'] = (
#             (df['Skor_Kapabilitas'] * 35) +  # History kecepatan paling ngaruh
#             (df['Skor_Attitude'] * 20) +
#             (df['Skor_Lokasi'] * 15) +       # Dekat lebih baik kalau buru2
#             (df['Skor_Usia'] * 10) +
#             (df['Skor_Spesialis'] * 20)
#         )
#         strategi_msg = f"🚀 **STRATEGI URGENT**: Fokus mencari penjahit dengan *History Speed* tinggi & Lokasi Efisien.\n\n{pesan_jarak}"
        
#         # Filter Cluster: Hanya tampilkan Elite & Standar (Buang yg perlu bimbingan)
#         df = df[df['Kategori_ML'] != 'Perlu Bimbingan']

#     else:
#         # STRATEGI SANTAI: Fokus Kerapian & Pemerataan
#         df['FINAL_SCORE'] = (
#             (df['Skor_Attitude'] * 40) +     # Kerapian nomor 1
#             (df['Skor_Spesialis'] * 20) +    # Kesesuaian skill
#             (df['Skor_Usia'] * 20) +         # Usia matang (rapi)
#             (df['Skor_Lokasi'] * 10) +
#             (df['Skor_Kapabilitas'] * 10)    # Kecepatan ga terlalu penting
#         )
#         strategi_msg = f"⚖️ **STRATEGI SANTAI**: Fokus Kualitas (Kerapian) & Pemerataan Order.\n\n{pesan_jarak}"

#     # 5. FORMAT OUTPUT
#     # ---------------------------------------------------------
#     # Urutkan ranking tertinggi
#     df_sorted = df.sort_values(by='FINAL_SCORE', ascending=False)
    
#     # Pilih kolom untuk ditampilkan
#     tampilan = [
#         'Nama', 
#         'Kategori_ML', 
#         'Spesialis', 
#         'Jarak Rumah ke Koperasi (Km)',
#         'Kerapian', # Bukti attitude
#         'FINAL_SCORE'
#     ]
    
#     # Tambahkan kolom history kecepatan agar user tahu alasannya
#     if kolom_kapabilitas:
#         tampilan.insert(4, 'Raw_Kapabilitas') # Tampilkan speed rata2 mereka

#     # Rename kolom biar cantik di web
#     rename_dict = {
#         'Raw_Kapabilitas': 'Est. Speed (Pcs/Hari)',
#         'Jarak Rumah ke Koperasi (Km)': 'Jarak (Km)'
#     }
    
#     return df_sorted[tampilan].rename(columns=rename_dict).head(10), strategi_msg

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

def hitung_rekomendasi(df_input, jenis_project, jumlah_pcs, kondisi_deadline):
    """
    Sistem Alokasi Penjahit Cerdas (Versi Standalone / Tanpa Database)
    """
    # 1. SETUP DATA
    # ---------------------------------------------------------
    df = df_input.copy()
    scaler = MinMaxScaler()
    
    # Mapping Input User ke Kolom Kapabilitas
    map_kapabilitas = {
        "Seragam Sekolah": ["Seragam Hem Putih (Pcs/hari)", "Seragam Hem Pramuka (Pcs/hari)"],
        "Seragam Pramuka": ["Seragam Hem Pramuka (Pcs/hari)", "Celana Pramuka Seragam (Pcs/hari)"],
        "Rok Seragam": ["Rok Seragam (Pcs/hari)"],
        "Kemeja/Batik": ["Kemeja Kerja (Pcs/hari)"],
        "Custom/Gamis/Sulit": ["Custom (Sulit) (Pcs/hari)"]
    }
    
    kolom_kapabilitas = map_kapabilitas.get(jenis_project, [])
    
    # 2. FILTERING AWAL
    # ---------------------------------------------------------
    if jenis_project == "Custom/Gamis/Sulit":
        df = df[df['Custom (Sulit) (Pcs/hari)'] > 0].copy()
        if df.empty:
            return df, "⚠️ Tidak ada penjahit yang memiliki history mengerjakan Custom/Sulit!"

    # 3. PERHITUNGAN SKOR
    # ---------------------------------------------------------
    
    # --- A. SKOR USIA ---
    df['Selisih_Usia'] = abs(df['Usia'] - 40)
    df['Skor_Usia'] = 1 - scaler.fit_transform(df[['Selisih_Usia']])

    # --- B. SKOR JARAK (BUG SUDAH DIPERBAIKI DISINI) ---
    df['Jarak_Norm'] = scaler.fit_transform(df[['Jarak Rumah ke Koperasi (Km)']])
    
    if jumlah_pcs < 20:
        # Order Kecil: Prioritas DEKAT
        df['Skor_Lokasi'] = 1 - df['Jarak_Norm'] 
        pesan_jarak = "📦 Order Kecil: Memprioritaskan penjahit TERDEKAT (hemat waktu)."
        
    elif jumlah_pcs > 50:
        # Order Besar: Jauh tidak masalah
        df['Skor_Lokasi'] = df['Jarak_Norm'] * 0.5 + 0.5 
        pesan_jarak = "🚛 Order Besar: Lokasi Jauh tidak masalah (sekali angkut)."
        
    else:
        # Order Menengah: Netral (BAGIAN INI YANG TADI BIKIN ERROR)
        df['Skor_Lokasi'] = 0.5 
        pesan_jarak = "⚖️ Order Menengah: Jarak tidak menjadi prioritas utama."

    # --- C. SKOR PERFORMA DASAR ---
    df['Skor_Attitude'] = (
        (df['Kerapian'] * 30) + 
        (df['Komitmen'] * 25) + 
        (df['Ketepatan Waktu'] * 20) 
    ) 

    # --- D. SKOR KAPABILITAS ---
    if kolom_kapabilitas:
        df['Raw_Kapabilitas'] = df[kolom_kapabilitas].mean(axis=1)
        df['Skor_Kapabilitas'] = scaler.fit_transform(df[['Raw_Kapabilitas']])
    else:
        df['Raw_Kapabilitas'] = 0 # Dummy untuk display
        df['Skor_Kapabilitas'] = 0.5 

    # --- E. SKOR SPESIALIS ---
    def hitung_match_spesialis(row):
        spesialis = str(row['Spesialis']).lower()
        project = jenis_project.lower()
        
        if "seragam" in project and "seragam" in spesialis and "semua" not in spesialis:
            return 1.0 
        elif "semua" in spesialis:
            return 0.8 
        elif "rok" in project and "rok" in spesialis:
            return 0.9
        else:
            return 0.2 
            
    df['Skor_Spesialis'] = df.apply(hitung_match_spesialis, axis=1)

    # 4. FINAL CALCULATION
    # ---------------------------------------------------------
    if kondisi_deadline == "Urgent (Buru-buru!)":
        df['FINAL_SCORE'] = (
            (df['Skor_Kapabilitas'] * 35) + 
            (df['Skor_Attitude'] * 20) +
            (df['Skor_Lokasi'] * 15) + 
            (df['Skor_Usia'] * 10) +
            (df['Skor_Spesialis'] * 20)
        )
        strategi_msg = f"🚀 **STRATEGI URGENT**: Fokus mencari penjahit dengan *History Speed* tinggi & Lokasi Efisien.\n\n{pesan_jarak}"
        
        # Filter: Hanya Elite & Standar
        df = df[df['Kategori_ML'] != 'Perlu Bimbingan']

    else:
        df['FINAL_SCORE'] = (
            (df['Skor_Attitude'] * 40) + 
            (df['Skor_Spesialis'] * 20) + 
            (df['Skor_Usia'] * 20) + 
            (df['Skor_Lokasi'] * 10) +
            (df['Skor_Kapabilitas'] * 10) 
        )
        strategi_msg = f"⚖️ **STRATEGI SANTAI**: Fokus Kualitas (Kerapian) & Pemerataan Order.\n\n{pesan_jarak}"

    # 5. FORMAT OUTPUT
    # ---------------------------------------------------------
    df_sorted = df.sort_values(by='FINAL_SCORE', ascending=False)
    
    tampilan = [
        'Nama', 
        'Kategori_ML', 
        'Spesialis', 
        'Jarak Rumah ke Koperasi (Km)',
        'Kerapian', 
        'FINAL_SCORE'
    ]
    
    if kolom_kapabilitas:
        tampilan.insert(4, 'Raw_Kapabilitas') 

    rename_dict = {
        'Raw_Kapabilitas': 'Est. Speed (Pcs/Hari)',
        'Jarak Rumah ke Koperasi (Km)': 'Jarak (Km)'
    }
    
    return df_sorted[tampilan].rename(columns=rename_dict).head(10), strategi_msg