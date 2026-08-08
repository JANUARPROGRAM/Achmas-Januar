"""
AstraLang Runtime (v0.1)
=========================
Berisi komponen-komponen yang dipakai saat program AstraLang benar-benar
dieksekusi:
- Environment: manajemen variable & scope (mendukung nested scope untuk
  function call, if-block, while-block).
- RuntimeError khusus AstraLang (AstraRuntimeError) supaya error dari
  program pengguna bisa dibedakan dari bug internal interpreter.
- Representasi nilai fungsi (AstraFunction) dan sinyal kontrol alur
  (ReturnSignal) yang dipakai interpreter untuk implementasi 'return'.
"""


class AstraRuntimeError(Exception):
    """Error yang terjadi saat eksekusi program AstraLang (bukan bug internal)."""

    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        if line is not None:
            super().__init__(f"[Runtime Error] Baris {line}: {message}")
        else:
            super().__init__(f"[Runtime Error] {message}")


class ReturnSignal(Exception):
    """Dipakai secara internal untuk 'melompat' keluar dari body fungsi saat 'return'."""

    def __init__(self, value):
        self.value = value


class Environment:
    """
    Menyimpan variable dalam satu scope, dengan pointer ke parent scope
    untuk mendukung lexical scoping (mis. variable global terlihat dari
    dalam function, tapi variable lokal function tidak bocor keluar).
    """

    def __init__(self, parent=None):
        self.vars = {}
        self.parent = parent

    def define(self, name, value):
        """Mendefinisikan variable baru di scope SAAT INI (dipakai oleh 'let')."""
        self.vars[name] = value

    def get(self, name, line=None):
        env = self
        while env is not None:
            if name in env.vars:
                return env.vars[name]
            env = env.parent
        raise AstraRuntimeError(f"Variabel '{name}' tidak ditemukan", line)

    def set(self, name, value, line=None):
        """Mengubah nilai variable yang SUDAH ADA (assignment tanpa 'let')."""
        env = self
        while env is not None:
            if name in env.vars:
                env.vars[name] = value
                return
            env = env.parent
        raise AstraRuntimeError(
            f"Tidak bisa assign ke variabel '{name}' yang belum dideklarasikan (gunakan 'let')",
            line,
        )


class AstraFunction:
    """Representasi runtime dari fungsi yang dideklarasikan dengan 'function'."""

    def __init__(self, declaration, closure_env):
        self.declaration = declaration  # FunctionDecl node
        self.closure_env = closure_env  # Environment saat fungsi didefinisikan

    @property
    def name(self):
        return self.declaration.name

    @property
    def arity(self):
        return len(self.declaration.params)

    def __repr__(self):
        return f"<function {self.name}>"


class AstraBuiltinFunction:
    """Wrapper untuk fungsi bawaan (built-in) yang diimplementasikan di Python."""

    def __init__(self, name, arity, py_func):
        self.name = name
        self.arity = arity  # -1 berarti argumen bebas
        self.py_func = py_func

    def __repr__(self):
        return f"<builtin function {self.name}>"
