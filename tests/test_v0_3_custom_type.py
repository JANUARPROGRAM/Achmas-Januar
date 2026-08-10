"""
Test Fitur Baru v0.3 Lanjutan: Custom Type
==============================================
Menguji:
- Deklarasi type (type Point { x y })
- Membuat instance (Point { x: 10, y: 20 })
- Akses field (p.x) dan field assignment (p.x = 99)
- Validasi: field tak dikenal, field belum diisi, type tak dikenal
- Kasus tepi: variabel huruf besar dipakai sebagai kondisi if/while
  (tidak boleh salah dikira instance literal)
- List literal multi-baris (bug yang ditemukan & diperbaiki di sesi ini)
- Kombinasi custom type dengan List (field berisi list, list berisi instance)

Cara jalankan:
    python3 tests/test_v0_3_custom_type.py
"""

import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_source, ParserError
from interpreter import Interpreter
from runtime import AstraRuntimeError

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


def run_and_capture(source):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        Interpreter().run(parse_source(source))
    return buf.getvalue()


def test_type_decl_and_instance():
    print("Test: deklarasi type & membuat instance")
    src = 'type Point {\n x\n y\n}\nlet p = Point { x: 10, y: 20 }\nprint p\n'
    out = run_and_capture(src)
    check("format print instance benar", out.strip() == "Point {x: 10, y: 20}")


def test_field_access():
    print("Test: akses field")
    src = 'type Point {\n x\n y\n}\nlet p = Point { x: 10, y: 20 }\nprint p.x\nprint p.y\n'
    out = run_and_capture(src)
    lines = out.strip().splitlines()
    check("field x benar", lines[0] == "10")
    check("field y benar", lines[1] == "20")


def test_field_assignment():
    print("Test: field assignment")
    src = 'type Point {\n x\n y\n}\nlet p = Point { x: 1, y: 2 }\np.x = 99\nprint p\n'
    out = run_and_capture(src)
    check("field berubah", out.strip() == "Point {x: 99, y: 2}")


def test_instance_with_list_field():
    print("Test: instance dengan field berisi List")
    src = '''
type Player {
    name
    scores
}
let pl = Player { name: "Astra", scores: [1, 2, 3] }
print pl.name
print pl.scores
push(pl.scores, 4)
print pl.scores
'''
    out = run_and_capture(src)
    lines = out.strip().splitlines()
    check("field string benar", lines[0] == "Astra")
    check("field list benar", lines[1] == "[1, 2, 3]")
    check("push ke field list benar", lines[2] == "[1, 2, 3, 4]")


def test_list_of_instances():
    print("Test: List berisi instance custom type")
    src = '''
type Item {
    nama
    harga
}
let keranjang = [
    Item { nama: "Buku", harga: 50000 },
    Item { nama: "Pensil", harga: 5000 }
]
let total = 0
let i = 0
while i < len(keranjang) {
    total = total + keranjang[i].harga
    i = i + 1
}
print total
'''
    out = run_and_capture(src)
    check("total dari list instance benar", out.strip() == "55000")


def test_type_as_function_param():
    print("Test: instance dipakai sebagai parameter fungsi")
    src = '''
type Point {
    x
    y
}
function jarak_x(a, b) {
    return a.x - b.x
}
let p1 = Point { x: 10, y: 0 }
let p2 = Point { x: 3, y: 0 }
print jarak_x(p1, p2)
'''
    out = run_and_capture(src)
    check("hasil fungsi dengan parameter instance benar", out.strip() == "7")


def test_unknown_field_in_instance_creation():
    print("Test: field tak dikenal saat membuat instance ditolak")
    try:
        run_and_capture('type Point {\n x\n y\n}\nlet p = Point { x: 1, z: 2 }\n')
        check("field tak dikenal ditolak", False)
    except AstraRuntimeError as e:
        check("field tak dikenal ditolak", True)
        check("hint menyebutkan field yang tersedia", "x, y" in e.hint)


def test_missing_field_in_instance_creation():
    print("Test: field belum diisi saat membuat instance ditolak")
    try:
        run_and_capture('type Point {\n x\n y\n}\nlet p = Point { x: 1 }\n')
        check("field belum diisi ditolak", False)
    except AstraRuntimeError as e:
        check("field belum diisi ditolak", True)
        check("pesan menyebutkan field y", "y" in e.message)


def test_access_unknown_field():
    print("Test: akses field yang tidak ada pada type ditolak")
    try:
        run_and_capture('type Point {\n x\n y\n}\nlet p = Point { x: 1, y: 2 }\nprint p.z\n')
        check("akses field tak dikenal ditolak", False)
    except AstraRuntimeError as e:
        check("akses field tak dikenal ditolak", True)


def test_undeclared_type():
    print("Test: membuat instance dari type yang belum dideklarasikan ditolak")
    try:
        run_and_capture('let p = TidakAda { x: 1 }\n')
        check("type tak dikenal ditolak", False)
    except AstraRuntimeError as e:
        check("type tak dikenal ditolak", True)
        check("hint menyarankan deklarasi type", "type TidakAda" in e.hint)


def test_field_access_on_non_instance():
    print("Test: field access pada nilai bukan instance ditolak")
    try:
        run_and_capture('let x = 5\nprint x.y\n')
        check("field access non-instance ditolak", False)
    except AstraRuntimeError as e:
        check("field access non-instance ditolak", True)


def test_type_decl_without_fields_rejected():
    print("Test: deklarasi type tanpa field ditolak di parser")
    try:
        parse_source('type Kosong {\n}\n')
        check("type tanpa field ditolak", False)
    except ParserError as e:
        check("type tanpa field ditolak", True)
        check("parser error punya hint", e.hint is not None)


def test_edge_case_uppercase_var_in_if_condition():
    print("Test: KASUS TEPI - variabel huruf besar sebagai kondisi if tidak rusak")
    src = 'let Aktif = true\nif Aktif {\n print "jalan normal"\n}\n'
    out = run_and_capture(src)
    check("if dengan variabel huruf besar tetap jalan normal", out.strip() == "jalan normal")


def test_edge_case_uppercase_var_in_while_condition():
    print("Test: KASUS TEPI - variabel huruf besar sebagai kondisi while tidak rusak")
    src = 'let Jalan = true\nlet hitung = 0\nwhile Jalan {\n hitung = hitung + 1\n Jalan = false\n}\nprint hitung\n'
    out = run_and_capture(src)
    check("while dengan variabel huruf besar tetap jalan normal", out.strip() == "1")


def test_multiline_list_literal():
    print("Test: BUG FIX - list literal multi-baris")
    src = '''
let daftar = [
    1,
    2,
    3
]
print daftar
'''
    out = run_and_capture(src)
    check("list multi-baris ter-parse benar", out.strip() == "[1, 2, 3]")


def test_multiline_list_with_trailing_comma():
    print("Test: list literal multi-baris dengan trailing comma")
    src = '''
let daftar = [
    1,
    2,
    3,
]
print daftar
'''
    out = run_and_capture(src)
    check("list multi-baris trailing comma benar", out.strip() == "[1, 2, 3]")


def test_regression_v0_1_and_v0_3_list_still_work():
    print("Test: regresi v0.1 (rekursi) dan v0.3 List tetap benar setelah custom type ditambahkan")
    src = '''
function faktorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * faktorial(n - 1)
    }
}
let a = [1, 2, 3]
push(a, 4)
print faktorial(5)
print a
'''
    out = run_and_capture(src)
    lines = out.strip().splitlines()
    check("faktorial tetap benar", lines[0] == "120")
    check("list tetap benar", lines[1] == "[1, 2, 3, 4]")


def main():
    print("=" * 60)
    print("MENJALANKAN TEST: CUSTOM TYPE (v0.3 lanjutan)")
    print("=" * 60)

    test_type_decl_and_instance()
    test_field_access()
    test_field_assignment()
    test_instance_with_list_field()
    test_list_of_instances()
    test_type_as_function_param()
    test_unknown_field_in_instance_creation()
    test_missing_field_in_instance_creation()
    test_access_unknown_field()
    test_undeclared_type()
    test_field_access_on_non_instance()
    test_type_decl_without_fields_rejected()
    test_edge_case_uppercase_var_in_if_condition()
    test_edge_case_uppercase_var_in_while_condition()
    test_multiline_list_literal()
    test_multiline_list_with_trailing_comma()
    test_regression_v0_1_and_v0_3_list_still_work()

    print("=" * 60)
    print(f"HASIL: {PASSED} lulus, {FAILED} gagal")
    print("=" * 60)
    return 1 if FAILED > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
