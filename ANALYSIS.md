# Analisis

## Mengapa thresholding diperlukan?

Thresholding diperlukan untuk mengubah citra grayscale menjadi citra biner sehingga piksel gelap yang diduga sebagai goresan tanda tangan dapat dipisahkan dari background. Setelah itu jumlah piksel foreground dapat dihitung dan digunakan untuk menentukan ada atau tidaknya tanda tangan.

## Perbandingan Global Threshold dan Otsu

Global threshold menggunakan nilai tetap `T = 180`, sehingga semua citra diproses dengan batas yang sama. Otsu menentukan nilai threshold secara otomatis berdasarkan distribusi intensitas pada citra.

Pada beberapa citra, global threshold dapat menghasilkan foreground yang terlalu banyak, terutama ketika pencahayaan atau warna background berbeda. Otsu dapat memberikan hasil yang lebih sesuai karena nilai threshold menyesuaikan kondisi citra.

Program memilih hasil Otsu sebagai hasil utama. Jika ROI hampir seragam atau foreground hasil Otsu terlalu besar dan dianggap tidak wajar, hasil global threshold digunakan sebagai fallback.

## Morphological Operation

Opening digunakan untuk mengurangi noise kecil setelah thresholding. Closing digunakan untuk menutup celah kecil sehingga goresan tanda tangan yang terputus dapat menjadi lebih menyatu.

## Aturan Keputusan

Foreground ratio dihitung dengan rumus:

`foreground ratio = jumlah piksel foreground / jumlah seluruh piksel ROI`

Aturan yang digunakan:

- `ratio >= 0.03` → `SIGNATURE PRESENT`
- `ratio < 0.03` → `SIGNATURE ABSENT`

## Jika Threshold Terlalu Tinggi atau Terlalu Rendah

Jika threshold terlalu tinggi, lebih banyak bagian background dapat masuk sebagai foreground sehingga jumlah piksel foreground menjadi terlalu besar.

Jika threshold terlalu rendah, bagian goresan tanda tangan yang tipis atau kurang gelap dapat hilang sehingga jumlah foreground menjadi terlalu kecil.

## Hasil Pengujian

Program menguji beberapa citra dengan tanda tangan dan beberapa citra tanpa tanda tangan. Hasil lengkap disimpan pada `outputs/results.csv`.

Catatan: citra `absent` pada project ini merupakan negative sample sintetis. Untuk pengujian yang lebih kuat, data tersebut dapat diganti dengan foto atau scan dokumen asli yang memang tidak memiliki tanda tangan.
