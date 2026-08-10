"""
Test Regresi Fitur Inti Bahasa (v0.1 Fondasi)
=================================================
Test ini memastikan fitur inti bahasa AstraLang (lexer, parser, interpreter
dasar) berjalan benar. Test ini WAJIB tetap lulus 100% di setiap versi
berikutnya (v0.3, v0.4, dst) — kalau ada yang gagal, berarti ada fitur lama
yang rusak dan harus diperbaiki sebelum lanjut.

Cara jalankan:
    python3 tests/test_v0_1_regression.py
"""

import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lexer import tokenize_source, LexerError
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


def test_lexer_basic():
    print("Test: Lexer dasar")
    tokens = tokenize_source('let x = 10\nprint "hello"\n')
    types = [t.type for t in tokens]
    check("token LET ada", "LET" in types)
    check("token STRING ada", "STRING" in types)
    check("token PRINT ada", "PRINT" in types)
    check("diakhiri EOF", types[-1] == "EOF")


def test_lexer_error():
    print("Test: Lexer error handling")
    try:
        tokenize_source('let x = @')
        check("karakter aneh melempar LexerError", False)
    except LexerError:
        check("karakter aneh melempar LexerError", True)


def test_parser_basic():
    print("Test: Parser dasar")
    ast = parse_source('let x = 1\nif x > 0 {\n print "a"\n} else {\n print "b"\n}\n')
    check("jumlah statement benar", len(ast.statements) == 2)


def test_parser_error():
    print("Test: Parser error handling")
    try:
        parse_source("let x = ")
        check("ekspresi kosong melempar ParserError", False)
    except ParserError:
        check("ekspresi kosong melempar ParserError", True)


def test_print_and_variable():
    print("Test: print & variable")
    out = run_and_capture('let nama = "Astra"\nprint nama\n')
    check("output benar", out.strip() == "Astra")


def test_arithmetic():
    print("Test: operasi matematika")
    out = run_and_capture('print 10 + 3\nprint 10 - 3\nprint 10 * 3\nprint 10 % 3\n')
    lines = out.strip().splitlines()
    check("penjumlahan", lines[0] == "13")
    check("pengurangan", lines[1] == "7")
    check("perkalian", lines[2] == "30")
    check("modulo", lines[3] == "1")


def test_division_by_zero():
    print("Test: pembagian dengan nol")
    try:
        run_and_capture("let a = 5 / 0")
        check("pembagian nol melempar error", False)
    except AstraRuntimeError:
        check("pembagian nol melempar error", True)


def test_if_else():
    print("Test: if/else")
    out = run_and_capture('let x = 10\nif x > 5 {\n print "besar"\n} else {\n print "kecil"\n}\n')
    check("cabang if terpilih", out.strip() == "besar")


def test_while_loop():
    print("Test: while loop")
    out = run_and_capture('let i = 1\nwhile i <= 3 {\n print i\n i = i + 1\n}\n')
    check("loop menghasilkan 1,2,3", out.strip().splitlines() == ["1", "2", "3"])


def test_function_and_recursion():
    print("Test: function & rekursi")
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
    check("faktorial(5) == 120", out.strip() == "120")


def test_logic_operators():
    print("Test: operator logika")
    out = run_and_capture('let x = 7\nif x > 5 and x < 10 {\n print "ok"\n}\n')
    check("and berfungsi", out.strip() == "ok")


def test_builtin_len():
    print("Test: built-in len()")
    out = run_and_capture('print len("AstraLang")')
    check("len() benar", out.strip() == "9")


def main():
    print("=" * 60)
    print("MENJALANKAN TEST REGRESI FITUR INTI BAHASA")
    print("=" * 60)

    test_lexer_basic()
    test_lexer_error()
    test_parser_basic()
    test_parser_error()
    test_print_and_variable()
    test_arithmetic()
    test_division_by_zero()
    test_if_else()
    test_while_loop()
    test_function_and_recursion()
    test_logic_operators()
    test_builtin_len()

    print("=" * 60)
    print(f"HASIL: {PASSED} lulus, {FAILED} gagal")
    print("=" * 60)
    return 1 if FAILED > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
