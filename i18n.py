"""
AstraLang i18n (v0.4)
========================
Sistem terjemahan sederhana untuk pesan error AstraLang. Semua pesan error
di source code (interpreter.py, parser.py, runtime.py) DITULIS dalam Bahasa
Indonesia sebagai bahasa kanonik/utama -- ini tidak berubah.

Modul ini menyediakan terjemahan ke Bahasa Inggris yang diterapkan HANYA
saat pesan ditampilkan ke pengguna (di compiler.py), berdasarkan pilihan
bahasa (--lang en). Pendekatan: kamus per-FRASA (bukan per-kalimat penuh),
supaya bisa menerjemahkan kalimat yang mengandung bagian dinamis (nama
variabel, angka, dll) tanpa perlu mendaftarkan setiap kombinasi kalimat.

Kalau ada frasa yang belum masuk kamus, frasa itu dibiarkan apa adanya
(Bahasa Indonesia) -- bukan error atau crash. Ini sesuai kesepakatan: lebih
baik sebagian pesan belum diterjemahkan sempurna daripada sistem yang rapuh.

Cara kerja translate(): mengganti substring yang cocok, dari frasa TERPANJANG
ke TERPENDEK, supaya frasa yang lebih spesifik tidak keburu "dimakan" oleh
frasa yang lebih pendek dan umum.
"""

# Kamus frasa Indonesia -> Inggris, diurutkan otomatis dari yang terpanjang
# saat proses translate (jadi urutan di sini tidak harus terurut manual).
PHRASE_DICTIONARY = {
    # --- Frasa umum lintas jenis error ---
    "tidak ditemukan": "not found",
    "tidak dikenal": "not recognized",
    "tidak dikenali": "not recognized",
    "tidak valid": "invalid",
    "membutuhkan tepat": "requires exactly",
    "membutuhkan": "requires",
    "diberikan": "given",
    "diharapkan": "expected",
    "Diharapkan": "Expected",

    # --- Variabel ---
    "Variabel": "Variable",
    "variabel": "variable",
    "belum dideklarasikan": "not declared yet",
    "sudah dipakai untuk sesuatu yang lain": "is already used for something else",

    # --- Tipe data ---
    "Tipe data tidak sesuai untuk": "Type mismatch for",
    "diharapkan angka, dapat": "expected a number, got",
    "hanya berlaku untuk": "only works for",
    "hanya mendukung": "only supports",
    "tidak mendukung tipe": "does not support type",

    # --- Operasi matematika ---
    "Nggak bisa membagi dengan angka nol": "Can't divide by zero",
    "Nggak bisa menghitung sisa bagi (%) dengan angka nol": "Can't compute remainder (%) with zero",
    "Tidak bisa membandingkan": "Can't compare",
    "dengan": "with",

    # --- List ---
    "Index list harus berupa integer": "List index must be an integer",
    "di luar jangkauan": "out of range",
    "list berisi": "the list has",
    "elemen": "elements",
    "List ini masih kosong": "This list is empty",
    "tidak ada index yang valid": "there is no valid index",
    "Tidak bisa pop() dari list yang kosong": "Can't pop() from an empty list",
    "Index yang valid untuk list ini adalah": "The valid index range for this list is",
    "sampai": "to",

    # --- Custom Type ---
    "tidak punya field": "doesn't have a field named",
    "Field yang tersedia pada": "Available fields on",
    "belum diisi saat membuat instance": "not filled in when creating the instance",
    "tidak dikenal pada type": "not recognized on type",
    "bukan sebuah type, tidak bisa dibuat instance-nya": "is not a type, can't create an instance of it",
    "Semua field wajib diisi saat membuat instance": "All fields must be filled in when creating an instance",

    # --- Fungsi ---
    "Fungsi": "Function",
    "argumen": "argument(s)",
    "bukan fungsi yang bisa dipanggil": "is not a callable function",
    "Hanya nama fungsi yang bisa dipanggil": "Only function names can be called",

    # --- File I/O ---
    "Gagal menulis file": "Failed to write file",
    "Gagal membaca file": "Failed to read file",
    "File": "File",
    "tidak ditemukan": "not found",

    # --- Struktur kode / parser ---
    "Token tidak terduga": "Unexpected token",
    "Struktur kode tidak valid": "Invalid code structure",
    "untuk menutup": "to close",
    "untuk membuka": "to open",
    "setelah": "after",
    "sebelum": "before",

    # --- Hint umum ---
    "Deklarasikan dulu dengan": "First declare it with",
    "sebelum dipakai": "before using it",
    "cek kemungkinan salah ketik nama variabel": "check for possible typos in the variable name",
    "Gunakan": "Use",
    "untuk mendeklarasikan variabel baru sebelum diberi nilai": "to declare a new variable before assigning a value",
    "Pastikan kedua operand bertipe integer atau float": "Make sure both operands are integers or floats",
    "Cek dulu apakah pembaginya nol sebelum membagi": "First check whether the divisor is zero before dividing",
    "Cek dulu apakah pembaginya nol sebelum memakai operator": "First check whether the divisor is zero before using the operator",
    "Cek dulu": "First check",
    "sebelum melakukan pembagian": "before dividing",
    "sebelum memakai operator": "before using the operator",
    "mis.": "e.g.",
    "atau": "or",
    "dan": "and",

    # --- Label sistem error (dipakai compiler.py) ---
    "Gagal membaca kode (Lexer Error):": "Failed to read code (Lexer Error):",
    "Struktur kode tidak valid (Parser Error):": "Invalid code structure (Parser Error):",
    "Terjadi error saat program berjalan (Runtime Error):": "An error occurred while running the program (Runtime Error):",
    "Command device ditolak (Permission Error):": "Device command denied (Permission Error):",
    "Runtime Error:": "Runtime Error:",
    "Lokasi:": "Location:",
    "Saran:": "Suggestion:",
    "Baris": "Line",
    "Kolom": "Column",

    # --- Pesan CLI (compiler.py) ---
    "File tidak ditemukan": "File not found",
    "Peringatan": "Warning",
    "tidak memakai ekstensi": "does not use the extension",
    "Melanjutkan tetap mencoba menjalankan...": "Continuing to try running it anyway...",
    "Terlalu banyak pemanggilan fungsi bersarang (kemungkinan rekursi tak berhenti).":
        "Too many nested function calls (likely a recursion that never stops).",
    "Cek apakah ada fungsi rekursif yang tidak punya kondisi berhenti (base case)":
        "Check whether there is a recursive function without a stopping condition (base case)",
}


def translate(text, lang="id"):
    """
    Menerjemahkan `text` ke bahasa `lang` ("id" atau "en") berdasarkan
    PHRASE_DICTIONARY. Kalau lang="id" atau text kosong, dikembalikan apa
    adanya. Frasa yang tidak dikenal dibiarkan tidak diterjemahkan (bukan
    error).
    """
    if lang != "en" or not text:
        return text

    result = text
    # Ganti dari frasa TERPANJANG ke TERPENDEK supaya frasa spesifik tidak
    # "dimakan duluan" oleh frasa pendek yang jadi bagian darinya.
    for phrase in sorted(PHRASE_DICTIONARY.keys(), key=len, reverse=True):
        if phrase in result:
            result = result.replace(phrase, PHRASE_DICTIONARY[phrase])
    return result


SUPPORTED_LANGUAGES = ("id", "en")


def normalize_lang(lang):
    """Validasi kode bahasa; kembalikan 'id' (default) kalau tidak dikenal."""
    if lang in SUPPORTED_LANGUAGES:
        return lang
    return "id"
