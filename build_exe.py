#!/usr/bin/env python3
"""
AstraLang Build Script — Membuat Executable (.exe)
======================================================
Script ini membungkus AstraLang (compiler.py + lexer.py + parser.py +
interpreter.py + runtime.py) menjadi SATU FILE EXECUTABLE yang bisa
dijalankan tanpa perlu install Python di komputer lain.

CATATAN JUJUR:
- Script ini memakai PyInstaller, yang HARUS di-install dulu dengan akses
  internet (pip install pyinstaller). Ini TIDAK bisa dijalankan di lingkungan
  tanpa akses internet.
- Hasil build BERBEDA per platform: menjalankan script ini di Windows
  menghasilkan file .exe untuk Windows; di Linux menghasilkan binary ELF
  untuk Linux; di Mac menghasilkan binary Mach-O untuk Mac. PyInstaller
  TIDAK bisa cross-compile (build .exe Windows dari Linux/Termux, atau
  sebaliknya) — build harus dilakukan di platform target aslinya.
- Untuk membuat AstraLang.exe yang jalan di Windows, script ini harus
  dijalankan DI KOMPUTER WINDOWS, bukan di Termux/Linux.

CARA PAKAI:
    1. Pastikan berada di folder root AstraLang (folder yang berisi
       compiler.py, lexer.py, parser.py, interpreter.py, runtime.py).
    2. Install PyInstaller (butuh internet):
           pip install pyinstaller
    3. Jalankan script ini:
           python3 build_exe.py
    4. Hasil executable akan ada di folder dist/
           Windows : dist/AstraLang.exe
           Linux   : dist/AstraLang
           Mac     : dist/AstraLang

Setelah itu, orang lain bisa menjalankan AstraLang TANPA perlu install
Python maupun AstraLang — cukup:
    Windows : AstraLang.exe main.as
    Linux   : ./AstraLang main.as
"""

import subprocess
import sys
import os
import shutil

REQUIRED_FILES = [
    "compiler.py", "lexer.py", "parser.py", "interpreter.py", "runtime.py",
]


def check_environment():
    """Verifikasi semua file AstraLang ada dan PyInstaller terpasang."""
    missing = [f for f in REQUIRED_FILES if not os.path.isfile(f)]
    if missing:
        print("ERROR: File AstraLang berikut tidak ditemukan di folder ini:")
        for f in missing:
            print(f"  - {f}")
        print("\nJalankan script ini dari folder root AstraLang.")
        return False

    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("ERROR: PyInstaller belum terpasang.")
        print("Install dulu dengan koneksi internet aktif:")
        print("  pip install pyinstaller")
        print("\nDi Termux, kalau pip biasa gagal, coba:")
        print("  pip install pyinstaller --break-system-packages")
        return False

    return True


def build():
    print("=" * 60)
    print("AstraLang Build Script — Membuat Executable")
    print("=" * 60)

    if not check_environment():
        sys.exit(1)

    print(f"\nPlatform terdeteksi: {sys.platform}")
    print("Memulai build dengan PyInstaller...\n")

    # --onefile   : bungkus semua jadi 1 file executable
    # --name      : nama file hasil build
    # compiler.py : entry point yang dibungkus (dia mengimpor lexer/parser/
    #               interpreter/runtime, jadi semuanya otomatis ikut terbawa)
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "AstraLang",
        "--console",
        "compiler.py",
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print("\nBuild GAGAL. Cek pesan error PyInstaller di atas.")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("BUILD SELESAI")
    print("=" * 60)
    dist_path = os.path.join("dist", "AstraLang.exe" if sys.platform == "win32" else "AstraLang")
    print(f"Executable ada di: {dist_path}")
    print("\nCara menjalankan:")
    if sys.platform == "win32":
        print("  AstraLang.exe examples\\hello.as")
    else:
        print("  ./dist/AstraLang examples/hello.as")
    print("\nFile ini bisa disalin & dijalankan di komputer lain (platform")
    print("yang sama) TANPA perlu install Python atau AstraLang lagi.")

    # Bersihkan folder build sementara (bukan dist/, itu hasil akhirnya)
    for temp_dir in ("build", "__pycache__"):
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)
    spec_file = "AstraLang.spec"
    if os.path.isfile(spec_file):
        os.remove(spec_file)


if __name__ == "__main__":
    build()
