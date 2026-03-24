import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans

def run_ml_process():
    print("--- MULAI FEATURE ENGINEERING & TRAINING ---")
    
    # 1. Load Data Bersih
    try:
        df = pd.read_excel('DATA CLEANED.xlsx')
    except:
        print("Error: File 'DATA CLEANED.xlsx' tidak ditemukan.")
        return

    # 2. Fitur untuk Clustering (Hanya kolom numerik performa)
    # Kita pakai kolom hasil cleaning sebelumnya
    features = ['Usia', 'Jarak Rumah ke Koperasi (Km)', 'Kerapian', 
                'Ketepatan Waktu', 'Quantity', 'Komitmen']
    
    X = df[features].copy()

    # 3. Normalisasi (Agar Usia 50 tidak memakan Jarak 2)
    scaler = MinMaxScaler()
    X_scaled = scaler.fit_transform(X)

    # 4. K-Means Clustering (k=3)
    print("-> Sedang melatih model K-Means...")
    kmeans = KMeans(n_clusters=3, random_state=42)
    df['Cluster_ID'] = kmeans.fit_predict(X_scaled)

    # 5. Analisis & Labeling Otomatis
    # Kita cari rata-rata tiap cluster untuk tahu mana yang "Elite"
    summary = df.groupby('Cluster_ID')[features].mean()
    
    # Logic: Cluster dengan Quantity & Ketepatan tertinggi adalah Elite
    # Cluster dengan Kerapian terendah adalah Perlu Bimbingan
    best_id = summary['Quantity'].idxmax()
    worst_id = summary['Kerapian'].idxmin()

    def get_label(c_id):
        if c_id == best_id:
            return "Elite Team (Cepat & Banyak)"
        elif c_id == worst_id:
            return "Perlu Bimbingan"
        else:
            return "Standar / Rapi"

    df['Kategori_ML'] = df['Cluster_ID'].apply(get_label)

    # 6. Simpan Hasil Akhir untuk Aplikasi
    output_file = 'DATA_FINAL_CLUSTERED.csv'
    df.to_csv(output_file, index=False)
    print(f"-> SUKSES! Data berlabel ML disimpan ke: {output_file}")
    print(df[['Nama', 'Kategori_ML']].head())

if __name__ == "__main__":
    run_ml_process()