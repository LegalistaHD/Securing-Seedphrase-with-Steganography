# Securing Seedphrase with Steganography

Aplikasi prototipe berbasis web (Streamlit) untuk mengamankan Kunci Pemulihan (Seed Phrase) Wallet Cryptocurrency berstandar BIP39 ke dalam citra digital menggunakan teknik steganografi. Aplikasi ini mengevaluasi dan membandingkan kinerja dua metode: **LSB Random** dan **Randomized Adaptive Edge-Based**.

---

## 📁 Struktur Direktori

Berdasarkan repositori ini, berikut adalah struktur file dan folder yang tersedia:

* `app.py`          : File utama untuk menjalankan aplikasi Streamlit.
* `requirements.txt`: Daftar pustaka (library) Python yang dibutuhkan.
* `core/`           : Modul algoritma inti steganografi, konversi BIP39, dan evaluasi metrik.
* `pages/`          : Modul antarmuka web (UI) untuk setiap fungsionalitas menu.
* `dataset/`        : Direktori untuk menyimpan citra pengujian (Cover Image).
* `assets/`         : Direktori untuk menyimpan aset statis pendukung aplikasi.
* `assets.zip`      : File cadangan kompresi untuk aset.

---

## ⚙️ Prasyarat (Prerequisites)

Sebelum menjalankan aplikasi, pastikan komputer/laptop Anda telah terinstal:
1. Python versi 3.9 atau yang lebih baru.
2. Pip (Python Package Installer).

---

## 🚀 Instruksi Instalasi

Ikuti langkah-langkah di bawah ini untuk menginstal dan menjalankan aplikasi secara lokal:

### Langkah 1: Ekstrak File
Jika Anda menerima proyek ini dalam bentuk file `.zip`, ekstrak seluruh isinya ke dalam satu folder di komputer Anda.

### Langkah 2: Buka Terminal / Command Prompt
Buka direktori folder hasil ekstrak tersebut. Klik kanan pada area kosong di dalam folder, lalu pilih "Open in Terminal". 
(Alternatif untuk Windows: Ketik `cmd` pada address bar folder tersebut, lalu tekan Enter).

### Langkah 3: Buat Virtual Environment (Sangat Direkomendasikan)
Untuk mencegah bentrok antar versi library di komputer Anda, buat environment terisolasi dengan mengetikkan perintah berikut di terminal:

python -m venv env

### Langkah 4: Aktifkan Virtual Environment
Aktifkan environment yang baru saja dibuat.
* Untuk pengguna Windows, ketik perintah:
  env\Scripts\activate

* Untuk pengguna Linux / Mac OS, ketik perintah:
  source env/bin/activate

### Langkah 5: Instal Dependensi (Library)
Setelah virtual environment aktif (biasanya ditandai dengan tulisan `(env)` di awal baris terminal), instal semua pustaka yang dibutuhkan dengan menjalankan perintah berikut:

pip install -r requirements.txt

---

## ▶️ Cara Menjalankan Aplikasi

Setelah proses instalasi selesai, Anda dapat langsung menjalankan aplikasi web dengan perintah berikut di dalam terminal:

streamlit run app.py

Aplikasi akan otomatis terbuka di browser utama Anda melalui alamat lokal (umumnya di http://localhost:8501).

---

## 💡 Fitur Utama

1. Modul Konversi BIP39: Menerjemahkan 12 kata Mnemonic menjadi 132-bit entropi biner murni secara efisien.
2. Metode LSB Random: Penyisipan pesan terenkripsi secara acak buta pada domain spasial gambar.
3. Metode Edge-Based: Penyisipan data secara adaptif memanfaatkan algoritma Canny Edge Detection untuk menyamarkan pesan pada tekstur kontur objek.
4. Perbandingan Kinerja: Eksekusi visualisasi kedua metode secara paralel untuk komparasi metrik.
5. Ultimate Stress Test: Pengujian otomatis (batch processing) untuk mengevaluasi kualitas citra (PSNR & SSIM), ketahanan manipulasi visual, waktu komputasi, dan keamanan steganografi menggunakan Chi-Square Attack.
