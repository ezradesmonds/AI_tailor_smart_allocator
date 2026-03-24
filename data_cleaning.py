import pandas as pd
import numpy as np
import os
import re

# ==========================================
# 1. SETUP & LOAD DATA
# ==========================================
input_file = 'Data koperasi/MERGE DATA PENJAHIT.xlsx'
output_file = 'DATA CLEANED.xlsx'

if not os.path.exists(input_file):
    print(f"ERROR: File '{input_file}' tidak ditemukan!")
    exit()

print(f"--- MEMULAI FINAL CLEANING ---")
print(f"Membaca file: {input_file}...")
df = pd.read_excel(input_file)
print(f"Total data awal: {len(df)} baris")

# ==========================================
# 2. HAPUS KOLOM & BARIS (FILTERING)
# ==========================================

# A. HAPUS KOLOM (NIK & Keluarga Miskin)
cols_to_drop = ['NIK', 'Status Keluarga Miskin']
existing_drop = [c for c in cols_to_drop if c in df.columns]
if existing_drop:
    df.drop(columns=existing_drop, inplace=True)
    print(f"-> Kolom dihapus: {existing_drop}")

# B. HAPUS BARIS (Status Non Aktif / Alm)
# Cari kolom yang mengandung kata 'Status'
status_col = next((c for c in df.columns if 'status' in c.lower()), None)

if status_col:
    print(f"-> Filter status pada kolom: '{status_col}'")
    # Regex untuk menangkap 'Non Aktif' atau 'Alm' (case insensitive)
    mask_buang = df[status_col].astype(str).str.contains(r'(non\s*aktif|alm)', case=False, regex=True, na=False)
    jumlah_dihapus = mask_buang.sum()
    df = df[~mask_buang].copy()
    print(f"-> {jumlah_dihapus} penjahit (Non Aktif/Alm) telah dihapus.")
else:
    print("WARNING: Kolom 'Status' tidak ditemukan otomatis. Pastikan nama kolomnya benar.")

# ==========================================
# 3. LOGIKA PEMBERSIHAN DATA (CLEANING)
# ==========================================

# DAFTAR KOLOM TEKS (Yang TIDAK BOLEH diubah jadi angka 0)
# Kita masukkan No, Nama, Kode, Alamat, dan kolom Kategori/Spesialis
cols_text_identity = ['No', 'Nama', 'Kode Penjahit', 'Alamat', 'Status', 'Keterangan']

# Fungsi Pembersih Angka (Sangat Kuat)
def clean_numeric_value(val):
    s = str(val).strip().lower()
    
    # 1. Cek Strip / Kosong / Nan -> Jadi 0
    if s in ['-', '–', '', 'nan', 'none']:
        return 0
    
    # 2. Cek True/False -> Jadi 1/0
    if s == 'true': return 1
    if s == 'false': return 0
    
    # 3. Cek Angka dengan Koma (untuk Jarak)
    s = s.replace(',', '.') 
    s = s.replace('km', '') # Buang satuan jika ada
    
    # 4. Convert ke Float/Int
    try:
        angka = float(s)
        # Jika belakangnya .0 (misal 5.0), jadikan integer 5 biar rapi
        if angka.is_integer():
            return int(angka)
        return angka
    except:
        return 0 # Jika error (misal teks aneh), anggap 0

# --- A. BERSIHKAN SEMUA KOLOM ANGKA (Jarak, Kerapian, Seragam, Kemeja, dll) ---
# Logic: Semua kolom KECUALI kolom identitas dan kolom Kategori/Spesialis
cols_exclude = cols_text_identity + [c for c in df.columns if 'kategori' in c.lower() or 'spesialis' in c.lower()]
cols_numeric = [c for c in df.columns if c not in cols_exclude]

print(f"-> Membersihkan {len(cols_numeric)} kolom angka (termasuk kemampuan jahit)...")
for col in cols_numeric:
    # Terapkan fungsi pembersih ke setiap sel
    df[col] = df[col].apply(clean_numeric_value)

# --- B. HANDLING SPESIALIS ---
# Cari kolom yang namanya mengandung 'spesialis'
col_spesialis = [c for c in df.columns if 'spesialis' in c.lower()]
txt_spesialis = "Hanya bisa mengerjakan rok, atasan dan celana"

for col in col_spesialis:
    df[col] = df[col].astype(str)
    # Ganti strip, nan, 0, atau kosong dengan teks panjang
    df[col] = df[col].replace(r'^\s*[-–]\s*$', txt_spesialis, regex=True) # Regex menangkap strip
    df[col] = df[col].replace(['nan', 'None', '0', '0.0', ''], txt_spesialis)
    print(f"-> Kolom '{col}' dibersihkan (Default: {txt_spesialis})")

# --- C. HANDLING KATEGORI (1 & 2) ---
# Cari kolom yang namanya mengandung 'kategori'
col_kategori = [c for c in df.columns if 'kategori' in c.lower()]
txt_kategori = "Tidak ada"

for col in col_kategori:
    df[col] = df[col].astype(str)
    # Ganti strip dengan "Tidak ada"
    df[col] = df[col].replace(r'^\s*[-–]\s*$', txt_kategori, regex=True)
    df[col] = df[col].replace(['nan', 'None', '0', '0.0', ''], txt_kategori)
    print(f"-> Kolom '{col}' dibersihkan (Default: {txt_kategori})")

# ==========================================
# 4. EXPORT FINAL
# ==========================================
print(f"-> Menyimpan file ke {output_file}...")
df.to_excel(output_file, index=False)

print("\n" + "="*50)
print(f"SUKSES! Data bersih tersimpan.")
print(f"Total Baris Akhir: {len(df)}")
print("="*50)