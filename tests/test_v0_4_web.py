"""
Test Fitur Baru v0.4: Web & File I/O
=======================================
Menguji:
- write_file() / read_file() -- fondasi untuk generate HTML/file apa pun
- str() -- konversi eksplisit ke string
- serve_html() -- web server bawaan (http.server stdlib), diuji dengan
  request HTTP sungguhan ke localhost, bukan simulasi
- Perbaikan parser: ekspresi + / - multi-baris (dibutuhkan untuk menyusun
  string HTML panjang secara natural)

Cara jalankan:
    python3 tests/test_v0_4_web.py
"""

import sys
import os
import io
import contextlib
import threading
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parser import parse_source
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


def test_write_and_read_file(tmp_dir):
    print("Test: write_file() dan read_file()")
    path = os.path.join(tmp_dir, "test_v0_4_a.txt")
    src = f'write_file("{path}", "halo dari astralang")\nlet isi = read_file("{path}")\nprint isi\n'
    out = run_and_capture(src)
    check("isi file benar", out.strip() == "halo dari astralang")
    check("file benar-benar ada di disk", os.path.isfile(path))
    if os.path.isfile(path):
        os.remove(path)


def test_write_file_non_string_content(tmp_dir):
    print("Test: write_file() menerima non-string dan mengonversinya otomatis")
    path = os.path.join(tmp_dir, "test_v0_4_b.txt")
    src = f'write_file("{path}", 12345)\nprint read_file("{path}")\n'
    out = run_and_capture(src)
    check("angka dikonversi ke string saat ditulis", out.strip() == "12345")
    if os.path.isfile(path):
        os.remove(path)


def test_read_file_not_found():
    print("Test: read_file() untuk file yang tidak ada melempar error dengan hint")
    try:
        run_and_capture('print read_file("/path/tidak/ada/sama/sekali.txt")')
        check("file tidak ditemukan melempar error", False)
    except AstraRuntimeError as e:
        check("file tidak ditemukan melempar error", True)
        check("error punya hint", e.hint is not None)


def test_str_builtin():
    print("Test: str() built-in")
    out = run_and_capture('print str(123)\nprint str(true)\nprint str(null)\n')
    lines = out.strip().splitlines()
    check("str(123)", lines[0] == "123")
    check("str(true)", lines[1] == "true")
    check("str(null)", lines[2] == "null")


def test_multiline_string_concat_with_plus():
    print("Test: BUG FIX - ekspresi + multi-baris (untuk menyusun HTML panjang)")
    src = '''
let html = "<a>" +
    "<b>" +
    "<c>"
print html
'''
    out = run_and_capture(src)
    check("string tergabung benar", out.strip() == "<a><b><c>")


def test_html_generation_with_loop(tmp_dir):
    print("Test: generate HTML dari List lewat loop (skenario web_demo.as)")
    path = os.path.join(tmp_dir, "test_v0_4_gen.html")
    src = f'''
let daftar = ["A", "B", "C"]
let item_html = ""
let i = 0
while i < len(daftar) {{
    item_html = item_html + "<li>" + daftar[i] + "</li>"
    i = i + 1
}}
let html = "<ul>" + item_html + "</ul>"
write_file("{path}", html)
'''
    run_and_capture(src)
    check("file HTML ada", os.path.isfile(path))
    if os.path.isfile(path):
        with open(path) as f:
            content = f.read()
        check("isi HTML benar", content == "<ul><li>A</li><li>B</li><li>C</li></ul>")
        os.remove(path)


def test_serve_html_real_http_request():
    print("Test: serve_html() -- web server NYATA, diuji lewat HTTP request sungguhan")
    port = 48601
    src = f'''
let html = "<html><body><h1>Test Server AstraLang</h1></body></html>"
serve_html(html, {port})
'''
    interp = Interpreter()
    t = threading.Thread(target=lambda: interp.run(parse_source(src)), daemon=True)
    t.start()
    time.sleep(0.5)
    try:
        resp = urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=3)
        body = resp.read().decode("utf-8")
        check("status HTTP 200", resp.status == 200)
        check("isi body benar", "Test Server AstraLang" in body)
        check("content-type html", "text/html" in resp.headers.get("Content-Type", ""))
    except Exception as e:
        check(f"request ke server gagal: {e}", False)


def test_serve_html_rejects_invalid_port():
    print("Test: serve_html() menolak port bukan integer")
    try:
        run_and_capture('serve_html("<h1>x</h1>", "bukan_port")')
        check("port non-integer ditolak", False)
    except AstraRuntimeError as e:
        check("port non-integer ditolak", True)


def test_regression_still_works():
    print("Test: regresi v0.1/v0.3 tetap benar setelah fitur web ditambahkan")
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
print faktorial(5)
print p.x + p.y
'''
    out = run_and_capture(src)
    lines = out.strip().splitlines()
    check("faktorial tetap benar", lines[0] == "120")
    check("custom type tetap benar", lines[1] == "3")


def main():
    import tempfile
    tmp_dir = tempfile.mkdtemp(prefix="astralang_test_")

    print("=" * 60)
    print("MENJALANKAN TEST: WEB & FILE I/O (v0.4)")
    print("=" * 60)

    test_write_and_read_file(tmp_dir)
    test_write_file_non_string_content(tmp_dir)
    test_read_file_not_found()
    test_str_builtin()
    test_multiline_string_concat_with_plus()
    test_html_generation_with_loop(tmp_dir)
    test_serve_html_real_http_request()
    test_serve_html_rejects_invalid_port()
    test_regression_still_works()

    print("=" * 60)
    print(f"HASIL: {PASSED} lulus, {FAILED} gagal")
    print("=" * 60)

    import shutil
    shutil.rmtree(tmp_dir, ignore_errors=True)

    return 1 if FAILED > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
