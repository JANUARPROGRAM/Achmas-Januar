"""
AstraLang Parser (v0.1)
========================
Mengubah deretan Token dari Lexer menjadi Abstract Syntax Tree (AST).
Menggunakan teknik recursive-descent parsing dengan precedence climbing
untuk ekspresi matematika/logika.

Semua node AST didefinisikan sebagai class kecil (bukan dict) supaya
mudah dibaca dan dikembangkan oleh interpreter.
"""

from lexer import Lexer


class ParserError(Exception):
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        super().__init__(f"[Parser Error] Baris {line}, Kolom {column}: {message}")


# ---------------------------------------------------------------------------
# AST Node definitions
# ---------------------------------------------------------------------------
class Node:
    """Base class, hanya untuk penanda tipe."""
    pass


class Program(Node):
    def __init__(self, statements):
        self.statements = statements


class LetStatement(Node):
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line


class PrintStatement(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class IfStatement(Node):
    def __init__(self, condition, then_branch, else_branch, line):
        self.condition = condition
        self.then_branch = then_branch    # list of statements
        self.else_branch = else_branch    # list of statements or None
        self.line = line


class WhileStatement(Node):
    def __init__(self, condition, body, line):
        self.condition = condition
        self.body = body
        self.line = line


class FunctionDecl(Node):
    def __init__(self, name, params, body, line):
        self.name = name
        self.params = params
        self.body = body
        self.line = line


class ReturnStatement(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class ExpressionStatement(Node):
    def __init__(self, expr, line):
        self.expr = expr
        self.line = line


class AssignExpr(Node):
    def __init__(self, name, value, line):
        self.name = name
        self.value = value
        self.line = line


class BinaryExpr(Node):
    def __init__(self, left, op, right, line):
        self.left = left
        self.op = op
        self.right = right
        self.line = line


class UnaryExpr(Node):
    def __init__(self, op, operand, line):
        self.op = op
        self.operand = operand
        self.line = line


class LiteralExpr(Node):
    def __init__(self, value, line):
        self.value = value
        self.line = line


class VarExpr(Node):
    def __init__(self, name, line):
        self.name = name
        self.line = line


class CallExpr(Node):
    def __init__(self, callee, args, line):
        self.callee = callee
        self.args = args
        self.line = line


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # -- helper dasar ---------------------------------------------------
    def _peek(self, offset=0):
        idx = self.pos + offset
        if idx < len(self.tokens):
            return self.tokens[idx]
        return self.tokens[-1]  # EOF

    def _current(self):
        return self._peek()

    def _advance(self):
        tok = self.tokens[self.pos]
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
        return tok

    def _check(self, type_):
        return self._current().type == type_

    def _match(self, *types):
        if self._current().type in types:
            return self._advance()
        return None

    def _expect(self, type_, message):
        if self._check(type_):
            return self._advance()
        tok = self._current()
        raise ParserError(message, tok.line, tok.column)

    def _skip_newlines(self):
        while self._check("NEWLINE") or self._check("SEMI"):
            self._advance()

    # -- entry point ------------------------------------------------------
    def parse(self):
        statements = []
        self._skip_newlines()
        while not self._check("EOF"):
            statements.append(self._statement())
            self._skip_newlines()
        return Program(statements)

    # -- statements ---------------------------------------------------------
    def _statement(self):
        tok = self._current()

        if tok.type == "LET":
            return self._let_statement()
        if tok.type == "PRINT":
            return self._print_statement()
        if tok.type == "IF":
            return self._if_statement()
        if tok.type == "WHILE":
            return self._while_statement()
        if tok.type == "FUNCTION":
            return self._function_decl()
        if tok.type == "RETURN":
            return self._return_statement()

        return self._expression_statement()

    def _let_statement(self):
        line = self._current().line
        self._advance()  # 'let'
        name_tok = self._expect("IDENT", "Diharapkan nama variabel setelah 'let'")
        self._expect("ASSIGN", f"Diharapkan '=' setelah nama variabel '{name_tok.value}'")
        value = self._expression()
        return LetStatement(name_tok.value, value, line)

    def _print_statement(self):
        line = self._current().line
        self._advance()  # 'print'
        value = self._expression()
        return PrintStatement(value, line)

    def _block(self):
        """Mem-parse blok { ... } dan mengembalikan list statement."""
        self._expect("LBRACE", "Diharapkan '{' untuk memulai blok")
        self._skip_newlines()
        statements = []
        while not self._check("RBRACE") and not self._check("EOF"):
            statements.append(self._statement())
            self._skip_newlines()
        self._expect("RBRACE", "Diharapkan '}' untuk menutup blok")
        return statements

    def _if_statement(self):
        line = self._current().line
        self._advance()  # 'if'
        condition = self._expression()
        then_branch = self._block()
        else_branch = None
        self._skip_newlines_peek_else()
        if self._check("ELSE"):
            self._advance()
            if self._check("IF"):
                else_branch = [self._if_statement()]
            else:
                else_branch = self._block()
        return IfStatement(condition, then_branch, else_branch, line)

    def _skip_newlines_peek_else(self):
        # Izinkan newline sebelum 'else' tanpa memakannya kalau bukan else
        save = self.pos
        while self._check("NEWLINE"):
            self._advance()
        if not self._check("ELSE"):
            self.pos = save

    def _while_statement(self):
        line = self._current().line
        self._advance()  # 'while'
        condition = self._expression()
        body = self._block()
        return WhileStatement(condition, body, line)

    def _function_decl(self):
        line = self._current().line
        self._advance()  # 'function'
        name_tok = self._expect("IDENT", "Diharapkan nama fungsi setelah 'function'")
        self._expect("LPAREN", f"Diharapkan '(' setelah nama fungsi '{name_tok.value}'")
        params = []
        if not self._check("RPAREN"):
            params.append(self._expect("IDENT", "Diharapkan nama parameter").value)
            while self._match("COMMA"):
                params.append(self._expect("IDENT", "Diharapkan nama parameter").value)
        self._expect("RPAREN", "Diharapkan ')' setelah daftar parameter")
        body = self._block()
        return FunctionDecl(name_tok.value, params, body, line)

    def _return_statement(self):
        line = self._current().line
        self._advance()  # 'return'
        value = None
        if not self._check("NEWLINE") and not self._check("RBRACE") and not self._check("EOF"):
            value = self._expression()
        return ReturnStatement(value, line)

    def _expression_statement(self):
        line = self._current().line
        expr = self._expression()
        return ExpressionStatement(expr, line)

    # -- expressions (precedence climbing) ---------------------------------
    def _expression(self):
        return self._assignment()

    def _assignment(self):
        expr = self._logic_or()
        if self._check("ASSIGN"):
            line = self._current().line
            self._advance()
            value = self._assignment()
            if isinstance(expr, VarExpr):
                return AssignExpr(expr.name, value, line)
            raise ParserError("Target assignment tidak valid", line, self._current().column)
        return expr

    def _logic_or(self):
        expr = self._logic_and()
        while self._check("OR"):
            op = self._advance()
            right = self._logic_and()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _logic_and(self):
        expr = self._equality()
        while self._check("AND"):
            op = self._advance()
            right = self._equality()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _equality(self):
        expr = self._comparison()
        while self._check("EQ") or self._check("NEQ"):
            op = self._advance()
            right = self._comparison()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _comparison(self):
        expr = self._term()
        while self._current().type in ("LT", "GT", "LTE", "GTE"):
            op = self._advance()
            right = self._term()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _term(self):
        expr = self._factor()
        while self._current().type in ("PLUS", "MINUS"):
            op = self._advance()
            right = self._factor()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _factor(self):
        expr = self._unary()
        while self._current().type in ("STAR", "SLASH", "PERCENT"):
            op = self._advance()
            right = self._unary()
            expr = BinaryExpr(expr, op.value, right, op.line)
        return expr

    def _unary(self):
        if self._current().type in ("MINUS", "NOT"):
            op = self._advance()
            operand = self._unary()
            return UnaryExpr(op.value, operand, op.line)
        return self._call()

    def _call(self):
        expr = self._primary()
        while True:
            if self._check("LPAREN"):
                line = self._current().line
                self._advance()
                args = []
                if not self._check("RPAREN"):
                    args.append(self._expression())
                    while self._match("COMMA"):
                        args.append(self._expression())
                self._expect("RPAREN", "Diharapkan ')' setelah argumen fungsi")
                expr = CallExpr(expr, args, line)
            else:
                break
        return expr

    def _primary(self):
        tok = self._current()

        if tok.type == "NUMBER":
            self._advance()
            return LiteralExpr(tok.value, tok.line)
        if tok.type == "STRING":
            self._advance()
            return LiteralExpr(tok.value, tok.line)
        if tok.type == "TRUE":
            self._advance()
            return LiteralExpr(True, tok.line)
        if tok.type == "FALSE":
            self._advance()
            return LiteralExpr(False, tok.line)
        if tok.type == "IDENT":
            self._advance()
            return VarExpr(tok.value, tok.line)
        if tok.type == "LPAREN":
            self._advance()
            expr = self._expression()
            self._expect("RPAREN", "Diharapkan ')' untuk menutup ekspresi")
            return expr

        raise ParserError(
            f"Token tidak terduga: {tok.type} ({tok.value!r})",
            tok.line, tok.column,
        )


def parse_source(source: str):
    """Fungsi bantu: source code string -> AST Program."""
    tokens = Lexer(source).tokenize()
    return Parser(tokens).parse()
