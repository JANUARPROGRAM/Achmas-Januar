# Panduan Build AstraLang jadi Executable

Dokumen ini menjelaskan cara mengemas AstraLang jadi satu file executable
(`.exe` di Windows, binary di Linux/Mac) yang bisa dijalankan orang lain
**tanpa perlu install Python atau AstraLang**.

---

## Kenapa Perlu Build Manual (Tidak Otomatis)

Proses build memakai [PyInstaller](https://pyinstaller.org/), yang:

1. **Butuh diinstall lewat internet** (`pip install pyinstaller`) — tidak
   bisa dijalankan di lingkungan tanpa akses internet.
2. **Tidak bisa cross-compile.** Menjalankan build di Linux menghasilkan
   binary Linux; menjalankan build di Windows menghasilkan `.exe` Windows;
   menjalankan build di Mac menghasilkan binary Mac. **Untuk mendapatkan
   `AstraLang.exe` yang jalan di Windows, proses build harus dilakukan DI
   KOMPUTER WINDOWS**, bukan di Termux atau Linux.

Karena dua alasan ini, build tidak bisa dilakukan otomatis dari lingkungan
pengembangan AstraLang — harus dijalankan manual oleh pengguna di platform
target.

---

## Cara Build

### Di Windows

1. Install Python 3.9+ dari [python.org](https://www.python.org/) (kalau
   belum ada).
2. Buka Command Prompt / PowerShell di folder `AstraLang/`.
3. Install PyInstaller:
   ```
   pip install pyinstaller
   ```
4. Jalankan script build:
   ```
   python build_exe.py
   ```
5. Hasil ada di `dist\AstraLang.exe`.
6. Jalankan:
   ```
   dist\AstraLang.exe examples\hello.as
   ```

### Di Linux / Termux

1. Pastikan Python 3 & pip terpasang:
   ```bash
   pkg install python -y     # Termux
   # atau: sudo apt install python3 python3-pip   # Linux biasa
   ```
2. Install PyInstaller (butuh internet):
   ```bash
   pip install pyinstaller --break-system-packages
   ```
3. Jalankan script build:
   ```bash
   python3 build_exe.py
   ```
4. Hasil ada di `dist/AstraLang`.
5. Jalankan:
   ```bash
   ./dist/AstraLang examples/hello.as
   ```

### Di Mac

Sama seperti Linux, tapi hasilnya adalah binary Mach-O untuk macOS.

---

## Distribusi Hasil Build

File di `dist/AstraLang` (atau `AstraLang.exe`) adalah **satu file mandiri**
— bisa disalin ke komputer lain dengan platform & arsitektur yang sama, dan
langsung dijalankan tanpa install apa pun:

```bash
AstraLang.exe main.as          # Windows
./AstraLang main.as             # Linux/Mac
```

---

## Batasan yang Perlu Diketahui

- **APK (Android) belum bisa dibuat** dari script ini atau dari lingkungan
  pengembangan AstraLang saat ini. Membuat APK butuh Android SDK, toolchain
  Java/Kotlin, dan proses build yang jauh berbeda dari PyInstaller. Ini
  dicatat sebagai keterbatasan jujur, bukan diklaim sudah bisa.
- Ukuran file hasil build biasanya cukup besar (puluhan MB) karena
  PyInstaller membundel seluruh interpreter Python di dalamnya — ini normal
  untuk semua program yang di-build dengan cara ini, bukan hal yang salah.
- Executable hasil build **hanya jalan di platform yang sama** dengan
  tempat ia di-build (lihat penjelasan cross-compile di atas).
- Fitur `serve_html()` (web server) tetap berfungsi normal di dalam
  executable hasil build, karena hanya memakai modul standar Python
  (`http.server`) yang otomatis ikut terbundel.
