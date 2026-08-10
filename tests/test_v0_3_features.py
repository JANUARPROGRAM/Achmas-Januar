"""
Test Fitur Baru v0.3: Type System & Error System
====================================================
Menguji:
- Tipe data List: literal, indexing, index assignment, push/pop/get, len()
- List bersarang (nested list)
- Nilai null sebagai literal eksplisit
- Error System: setiap error runtime/parser membawa hint (saran perbaikan)

Cara jalankan:
    python3 tests/test_v0_3_features.py
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


def test_list_literal_and_print():
    print("Test: List literal & print")
    out = run_and_capture("print [1, 2, 3]")
    check("format print benar", out.strip() == "[1, 2, 3]")


def test_list_indexing():
    print("Test: List indexing")
    out = run_and_capture('let a = [10, 20, 30]\nprint a[0]\nprint a[2]\n')
    lines = out.strip().splitlines()
    check("index 0 benar", lines[0] == "10")
    check("index 2 benar", lines[1] == "30")


def test_list_index_assignment():
    print("Test: List index assignment")
    out = run_and_capture('let a = [1, 2, 3]\na[1] = 99\nprint a\n')
    check("elemen berubah", out.strip() == "[1, 99, 3]")


def test_list_index_out_of_range():
    print("Test: List index out of range melempar error dengan hint")
    try:
        run_and_capture('let a = [1, 2, 3]\nprint a[10]\n')
        check("index out of range melempar error", False)
    except AstraRuntimeError as e:
        check("index out of range melempar error", True)
        check("error punya hint", e.hint is not None and len(e.hint) > 0)


def test_list_push_pop():
    print("Test: push() dan pop()")
    out = run_and_capture('let a = [1, 2]\npush(a, 3)\nprint a\nlet x = pop(a)\nprint x\nprint a\n')
    lines = out.strip().splitlines()
    check("push menambah elemen", lines[0] == "[1, 2, 3]")
    check("pop mengembalikan elemen terakhir", lines[1] == "3")
    check("pop menghapus dari list", lines[2] == "[1, 2]")


def test_list_get_builtin():
    print("Test: get() builtin")
    out = run_and_capture('let a = [5, 6, 7]\nprint get(a, 1)\n')
    check("get() benar", out.strip() == "6")


def test_list_len():
    print("Test: len() untuk List")
    out = run_and_capture('print len([1, 2, 3, 4])')
    check("len list benar", out.strip() == "4")


def test_nested_list():
    print("Test: List bersarang (nested list)")
    out = run_and_capture('let m = [[1, 2], [3, 4]]\nprint m[0][1]\nprint m[1][0]\n')
    lines = out.strip().splitlines()
    check("akses nested [0][1]", lines[0] == "2")
    check("akses nested [1][0]", lines[1] == "3")


def test_list_in_loop():
    print("Test: List dipakai dalam while loop")
    src = '''
let daftar = [10, 20, 30]
let i = 0
let total = 0
while i < len(daftar) {
    total = total + daftar[i]
    i = i + 1
}
print total
'''
    out = run_and_capture(src)
    check("total penjumlahan benar", out.strip() == "60")


def test_null_literal():
    print("Test: null sebagai literal")
    out = run_and_capture('let x = null\nprint x\n')
    check("print null benar", out.strip() == "null")


def test_null_comparison():
    print("Test: perbandingan dengan null")
    out = run_and_capture('let x = null\nif x == null {\n print "kosong"\n}\n')
    check("perbandingan null benar", out.strip() == "kosong")


def test_index_not_integer_error():
    print("Test: index bukan integer melempar error yang jelas")
    try:
        run_and_capture('let a = [1,2,3]\nprint a["x"]\n')
        check("index string ditolak", False)
    except AstraRuntimeError as e:
        check("index string ditolak", "integer" in e.message)


def test_pop_empty_list_error():
    print("Test: pop() dari list kosong melempar error dengan hint")
    try:
        run_and_capture('let a = []\npop(a)\n')
        check("pop list kosong ditolak", False)
    except AstraRuntimeError as e:
        check("pop list kosong ditolak", True)
        check("error punya hint", e.hint is not None)


def test_parser_error_has_hint():
    print("Test: ParserError untuk list tak tertutup punya hint")
    try:
        parse_source("let a = [1, 2")
        check("list tak tertutup ditolak", False)
    except ParserError as e:
        check("list tak tertutup ditolak", True)
        check("parser error punya hint", e.hint is not None and "[" in e.hint)


def test_variable_not_found_has_hint():
    print("Test: variabel tidak ditemukan punya hint yang actionable")
    try:
        run_and_capture("print xxx")
        check("variabel tidak ditemukan ditolak", False)
    except AstraRuntimeError as e:
        check("variabel tidak ditemukan ditolak", True)
        check("hint menyebutkan 'let'", "let" in e.hint)


def test_trailing_comma_in_list():
    print("Test: trailing comma di list literal diperbolehkan")
    out = run_and_capture("print [1, 2, 3,]")
    check("trailing comma tidak error", out.strip() == "[1, 2, 3]")


def test_regression_still_works_with_list_added():
    print("Test: fitur v0.1 tidak rusak setelah List ditambahkan")
    src = '''
function faktorial(n) {
    if n <= 1 {
        return 1
    } else {
        return n * faktorial(n - 1)
    }
}
print faktorial(5)
'''
    out = run_and_capture(src)
    check("faktorial(5) == 120 tetap benar", out.strip() == "120")


def main():
    print("=" * 60)
    print("MENJALANKAN TEST: TYPE SYSTEM & ERROR SYSTEM (v0.3)")
    print("=" * 60)

    test_list_literal_and_print()
    test_list_indexing()
    test_list_index_assignment()
    test_list_index_out_of_range()
    test_list_push_pop()
    test_list_get_builtin()
    test_list_len()
    test_nested_list()
    test_list_in_loop()
    test_null_literal()
    test_null_comparison()
    test_index_not_integer_error()
    test_pop_empty_list_error()
    test_parser_error_has_hint()
    test_variable_not_found_has_hint()
    test_trailing_comma_in_list()
    test_regression_still_works_with_list_added()

    print("=" * 60)
    print(f"HASIL: {PASSED} lulus, {FAILED} gagal")
    print("=" * 60)
    return 1 if FAILED > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
