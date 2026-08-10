"""
Test Fitur Baru v0.4 Lanjutan: Kemudahan untuk Pemula
=========================================================
Menguji tiga fitur yang dibuat supaya AstraLang lebih gampang dari Python:
1. Variabel BOLEH tanpa 'let' (auto-declare), TANPA merusak closure/scope
2. Sistem pesan error bilingual (Indonesia/Inggris) lewat i18n.py
3. Built-in function siap pakai untuk pemula: input, random, randint,
   round, int, float

Cara jalankan:
    python3 tests/test_v0_4_beginner_friendly.py
"""

import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_source
from interpreter import Interpreter
from runtime import AstraRuntimeError
from i18n import translate, normalize_lang

PASSED = 0
FAILED = 0


def check(name, condition):
    global PASSED, FAILED
    if condition:
        PASSED += 1
        print(f"  [OK] {name}")
    else:
        FAILED += 1
        print(f"  [GAGAL] {name}")


def run_and_capture(source, stdin_text=None):
    buf = io.StringIO()
    if stdin_text is not None:
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(stdin_text)
        try:
            with contextlib.redirect_stdout(buf):
                Interpreter().run(parse_source(source))
        finally:
            sys.stdin = old_stdin
    else:
        with contextlib.redirect_stdout(buf):
            Interpreter().run(parse_source(source))
    return buf.getvalue()


# --- 1. Variabel tanpa 'let' ---

def test_variable_without_let():
    print("Test: variabel tanpa 'let' langsung jalan")
    out = run_and_capture('nama = "Budi"\nprint nama\n')
    check("assignment tanpa let bekerja", out.strip() == "Budi")


def test_mixed_let_and_no_let():
    print("Test: campuran variabel dengan dan tanpa 'let'")
    out = run_and_capture('let x = 10\ny = 20\nprint x + y\n')
    check("kombinasi let dan tanpa let benar", out.strip() == "30")


def test_closure_assignment_not_broken():
    print("Test: KRITIS - closure assignment (ubah variabel scope luar) TIDAK RUSAK")
    src = '''
let total = 0
function tambah() {
    total = total + 1
}
tambah()
tambah()
tambah()
print total
'''
    out = run_and_capture(src)
    check("closure assignment tetap mengubah variabel luar (bukan bikin baru)", out.strip() == "3")


def test_typo_in_expression_still_caught():
    print("Test: typo yang melibatkan pembacaan variabel tetap tertangkap sebagai error")
    src = '''
let counter = 0
function increment() {
    countr = countr + 1
}
increment()
'''
    try:
        run_and_capture(src)
        check("typo dengan pembacaan variabel tetap error", False)
    except AstraRuntimeError as e:
        check("typo dengan pembacaan variabel tetap error", "countr" in e.message)


def test_let_still_declares_locally():
    print("Test: 'let' tetap selalu mendeklarasikan di scope lokal (tidak berubah)")
    src = '''
let x = 1
function ubah() {
    let x = 99
}
ubah()
print x
'''
    out = run_and_capture(src)
    check("'let' di dalam function tidak bocor ke luar", out.strip() == "1")


# --- 2. Sistem bilingual ---

def test_translate_basic_phrases():
    print("Test: translate() menerjemahkan frasa yang dikenal")
    check("tidak ditemukan -> not found", translate("Variabel 'x' tidak ditemukan", "en") == "Variable 'x' not found")


def test_translate_unknown_stays_indonesian():
    print("Test: frasa tak dikenal dibiarkan apa adanya, tidak error")
    result = translate("ini frasa aneh yang tidak ada di kamus sama sekali xyz123", "en")
    check("tidak crash untuk frasa tak dikenal", isinstance(result, str))


def test_translate_id_passthrough():
    print("Test: lang='id' tidak mengubah teks sama sekali")
    original = "Variabel 'x' tidak ditemukan"
    check("id passthrough", translate(original, "id") == original)


def test_normalize_lang():
    print("Test: normalize_lang menolak nilai tak dikenal, fallback ke 'id'")
    check("lang valid 'en'", normalize_lang("en") == "en")
    check("lang valid 'id'", normalize_lang("id") == "id")
    check("lang tak dikenal fallback ke id", normalize_lang("xx") == "id")


def test_real_error_translated_end_to_end():
    print("Test: error runtime sungguhan diterjemahkan penuh (pesan + hint)")
    try:
        run_and_capture("let a = 5 / 0")
        check("harus melempar error", False)
    except AstraRuntimeError as e:
        msg_en = translate(e.message, "en")
        hint_en = translate(e.hint, "en")
        check("pesan diterjemahkan ke Inggris", "divide" in msg_en.lower() and "zero" in msg_en.lower())
        check("hint diterjemahkan ke Inggris", "divisor" in hint_en.lower())
        check("tidak ada sisa kata Indonesia jelas di pesan", "bisa" not in msg_en.lower())


# --- 3. Built-in pemula ---

def test_round_builtin():
    print("Test: round()")
    out = run_and_capture('print round(3.7)\nprint round(3.14159, 2)\n')
    lines = out.strip().splitlines()
    check("round tanpa desimal jadi integer", lines[0] == "4")
    check("round dengan desimal", lines[1] == "3.14")


def test_int_float_conversion():
    print("Test: int() dan float()")
    out = run_and_capture('print int("42")\nprint int(3.9)\nprint float("3.14")\nprint float(5)\n')
    lines = out.strip().splitlines()
    check("int dari string", lines[0] == "42")
    check("int dari float (truncate)", lines[1] == "3")
    check("float dari string", lines[2] == "3.14")
    check("float dari integer", lines[3] == "5.0")


def test_int_invalid_string_error():
    print("Test: int() dari string tidak valid melempar error dengan hint")
    try:
        run_and_capture('print int("bukan angka")')
        check("int string tidak valid ditolak", False)
    except AstraRuntimeError as e:
        check("int string tidak valid ditolak", True)
        check("error punya hint", e.hint is not None)


def test_randint_range():
    print("Test: randint() menghasilkan angka dalam range yang benar")
    src = '''
let semua_valid = true
let i = 0
while i < 20 {
    let x = randint(1, 5)
    if x < 1 {
        semua_valid = false
    }
    if x > 5 {
        semua_valid = false
    }
    i = i + 1
}
print semua_valid
'''
    out = run_and_capture(src)
    check("semua hasil randint dalam range 20x percobaan", out.strip() == "true")


def test_randint_invalid_range_error():
    print("Test: randint() dengan min > maks ditolak")
    try:
        run_and_capture("print randint(10, 1)")
        check("randint range terbalik ditolak", False)
    except AstraRuntimeError as e:
        check("randint range terbalik ditolak", True)


def test_random_range():
    print("Test: random() menghasilkan angka 0.0-1.0")
    src = '''
let semua_valid = true
let i = 0
while i < 10 {
    let r = random()
    if r < 0 {
        semua_valid = false
    }
    if r >= 1 {
        semua_valid = false
    }
    i = i + 1
}
print semua_valid
'''
    out = run_and_capture(src)
    check("semua hasil random dalam range", out.strip() == "true")


def test_input_builtin():
    print("Test: input() membaca stdin sungguhan")
    out = run_and_capture('let nama = input("Nama: ")\nprint "Halo, " + nama\n', stdin_text="Astra\n")
    check("input membaca dan dipakai dengan benar", "Halo, Astra" in out)


def test_full_guessing_game_scenario():
    print("Test: skenario lengkap ala pemula_demo.as (input + int + randint tidak dipakai, angka tetap)")
    src = '''
jawaban = 7
tebakan = 0
percobaan = 0
while tebakan != jawaban {
    let teks = input("Tebak: ")
    tebakan = int(teks)
    percobaan = percobaan + 1
}
print "Benar dalam " + str(percobaan) + " percobaan"
'''
    out = run_and_capture(src, stdin_text="3\n7\n")
    check("skenario game tebak angka selesai dengan benar", "Benar dalam 2 percobaan" in out)


def test_regression_after_all_v0_4_additions():
    print("Test: regresi total - v0.1/v0.3/v0.4 awal tetap benar")
    src = '''
function faktorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * faktorial(n - 1)
    }
}
type Point {
    x
    y
}
let p = Point { x: 1, y: 2 }
let daftar = [1, 2, 3]
push(daftar, 4)
print faktorial(5)
print p.x + p.y
print daftar
'''
    out = run_and_capture(src)
    lines = out.strip().splitlines()
    check("faktorial tetap benar", lines[0] == "120")
    check("custom type tetap benar", lines[1] == "3")
    check("list tetap benar", lines[2] == "[1, 2, 3, 4]")


def main():
    print("=" * 60)
    print("MENJALANKAN TEST: KEMUDAHAN PEMULA (v0.4 lanjutan)")
    print("=" * 60)

    test_variable_without_let()
    test_mixed_let_and_no_let()
    test_closure_assignment_not_broken()
    test_typo_in_expression_still_caught()
    test_let_still_declares_locally()

    test_translate_basic_phrases()
    test_translate_unknown_stays_indonesian()
    test_translate_id_passthrough()
    test_normalize_lang()
    test_real_error_translated_end_to_end()

    test_round_builtin()
    test_int_float_conversion()
    test_int_invalid_string_error()
    test_randint_range()
    test_randint_invalid_range_error()
    test_random_range()
    test_input_builtin()
    test_full_guessing_game_scenario()

    test_regression_after_all_v0_4_additions()

    print("=" * 60)
    print(f"HASIL: {PASSED} lulus, {FAILED} gagal")
    print("=" * 60)
    return 1 if FAILED > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
