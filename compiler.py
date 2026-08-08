"""
AstraLang Compiler/Runner - Entry Point (v0.1)
================================================
Ini adalah titik masuk (CLI) untuk menjalankan program AstraLang (.as).

Untuk v0.1, "compiler.py" sebenarnya berperan sebagai INTERPRETER RUNNER
(bukan compiler ke native code) — source dibaca -> lexer -> parser ->
interpreter dijalankan langsung. Nama "compiler.py" dipertahankan sebagai
entry point resmi karena roadmap v0.4+ akan menambahkan tahap kompilasi
sungguhan (mis. ke bytecode) tanpa mengubah cara pemakaian dari sisi user.

Cara pakai:
    python3 compiler.py <file.as>
    python3 compiler.py --version
"""

import sys
import os

from lexer import Lexer, LexerError
from parser import Parser, ParserError
from interpreter import Interpreter
from runtime import AstraRuntimeError

VERSION = "0.1.0"


def print_error_box(title, message):
    print(f"\n{title}", file=sys.stderr)
    print(f"  {message}", file=sys.stderr)


def run_file(path: str) -> int:
    if not os.path.isfile(path):
        print(f"Error: File tidak ditemukan: {path}", file=sys.stderr)
        return 1

    if not path.endswith(".as"):
        print(
            f"Peringatan: File '{path}' tidak memakai ekstensi '.as'. "
            "Melanjutkan tetap mencoba menjalankan...",
            file=sys.stderr,
        )

    with open(path, "r", encoding="utf-8") as f:
        source = f.read()

    # --- Tahap 1: Lexing ---
    try:
        tokens = Lexer(source).tokenize()
    except LexerError as e:
        print_error_box("Gagal membaca kode (Lexer Error):", e.message)
        print(f"  Lokasi: {path}:{e.line}:{e.column}", file=sys.stderr)
        return 1

    # --- Tahap 2: Parsing ---
    try:
        program = Parser(tokens).parse()
    except ParserError as e:
        print_error_box("Struktur kode tidak valid (Parser Error):", e.message)
        print(f"  Lokasi: {path}:{e.line}:{e.column}", file=sys.stderr)
        return 1

    # --- Tahap 3: Interpretasi ---
    try:
        Interpreter().run(program)
    except AstraRuntimeError as e:
        line_info = f":{e.line}" if e.line is not None else ""
        print_error_box("Terjadi error saat program berjalan (Runtime Error):", e.message)
        print(f"  Lokasi: {path}{line_info}", file=sys.stderr)
        return 1
    except RecursionError:
        print_error_box(
            "Runtime Error:",
            "Terlalu banyak pemanggilan fungsi bersarang (kemungkinan rekursi tak berhenti).",
        )
        return 1

    return 0


def print_usage():
    print("AstraLang - Bahasa Pemrograman Modern (Prototype)")
    print(f"Versi: {VERSION}")
    print()
    print("Cara pakai:")
    print("  python3 compiler.py <file.as>     Menjalankan file AstraLang")
    print("  python3 compiler.py --version     Menampilkan versi")
    print("  python3 compiler.py --help        Menampilkan bantuan ini")


def main():
    args = sys.argv[1:]

    if len(args) == 0 or args[0] in ("-h", "--help"):
        print_usage()
        return 0

    if args[0] in ("-v", "--version"):
        print(f"AstraLang v{VERSION}")
        return 0

    file_path = args[0]
    return run_file(file_path)


if __name__ == "__main__":
    sys.exit(main())
