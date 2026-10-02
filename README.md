# SiganturePCD

Mini project pengolahan citra untuk mendeteksi keberadaan tanda tangan pada area tanda tangan Dekan.

# Proses

1. Crop area tanda tangan.
2. Konversi ROI menjadi grayscale.
3. Thresholding dengan:
   - Global threshold (`T = 180`)
   - Otsu threshold
4. Membandingkan hasil thresholding.
5. Morphological operation:
   - Opening untuk mengurangi noise.
   - Closing untuk menutup celah kecil.
6. Menghitung jumlah piksel foreground dan foreground ratio.
7. Menentukan hasil:
   - `ratio >= 0.03` → `SIGNATURE PRESENT`
   - `ratio < 0.03` → `SIGNATURE ABSENT`
8. Jika hasil Otsu tidak wajar pada ROI kosong atau hampir seragam, digunakan global threshold sebagai fallback.

# Struktur Folder

```text
siganturepcd/
├── data/
│   └── test/
│       ├── present/
│       └── absent/
├── outputs/
├── src/
│   ├── __init__.py
│   └── signature_detector.py
├── run.py
├── requirements.txt
├── ANALYSIS.md
└── README.md
```

# How to Run

### 1. Masuk ke folder project

cd siganturepcd

### 2. Install library

pip install -r requirements.txt

### 3. Jalankan program

python run.py

Program akan menampilkan hasil klasifikasi di terminal.

Output yang dihasilkan:
- `outputs/results.csv` berisi hasil pengujian dan jumlah piksel foreground.
- `outputs/comparison_present.png` berisi perbandingan grayscale, global threshold, Otsu, dan morphology untuk citra dengan tanda tangan.
- `outputs/comparison_absent.png` berisi perbandingan untuk citra tanpa tanda tangan.

# Data Pengujian

Data `present` menggunakan beberapa crop tanda tangan yang diberikan. Data `absent` merupakan negative sample sintetis dengan area tanda tangan diganti menjadi area kertas kosong. Data ini digunakan untuk menguji aturan `SIGNATURE PRESENT` dan `SIGNATURE ABSENT`.

Hasil akurasi pada dataset contoh hanya berlaku untuk data pengujian tersebut.
