"""
AstraLang Interpreter (v0.1)
==============================
Tree-walking interpreter: berjalan langsung di atas AST hasil Parser.
Untuk v0.1 ini pendekatan tree-walking dipilih karena sederhana dan mudah
dikembangkan bertahap (v0.4 baru akan fokus ke kecepatan/compilation).

Fitur yang didukung:
- print
- variable (let, assignment)
- string, integer, float, boolean
- operasi matematika (+ - * / %) dan perbandingan
- kondisi (if / else)
- loop (while)
- function (deklarasi, pemanggilan, return, closure sederhana)
"""

from parser import (
    Program, LetStatement, PrintStatement, IfStatement, WhileStatement,
    FunctionDecl, ReturnStatement, ExpressionStatement,
    AssignExpr, BinaryExpr, UnaryExpr, LiteralExpr, VarExpr, CallExpr,
)
from runtime import (
    Environment, AstraRuntimeError, ReturnSignal,
    AstraFunction, AstraBuiltinFunction,
)


class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self._install_builtins()

    # -- built-in functions ------------------------------------------------
    def _install_builtins(self):
        def _len(args, line):
            if len(args) != 1:
                raise AstraRuntimeError("len() membutuhkan tepat 1 argumen", line)
            val = args[0]
            if isinstance(val, str):
                return len(val)
            raise AstraRuntimeError("len() hanya mendukung string di v0.1", line)

        self.global_env.define("len", AstraBuiltinFunction("len", 1, _len))

    # -- entry point ---------------------------------------------------------
    def run(self, program: Program):
        for stmt in program.statements:
            self._exec_statement(stmt, self.global_env)

    # -- statement execution ---------------------------------------------------
    def _exec_statement(self, stmt, env: Environment):
        method_name = f"_exec_{type(stmt).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise AstraRuntimeError(
                f"Statement tidak dikenal oleh interpreter: {type(stmt).__name__}"
            )
        return method(stmt, env)

    def _exec_LetStatement(self, stmt: LetStatement, env: Environment):
        value = self._eval(stmt.value, env)
        env.define(stmt.name, value)

    def _exec_PrintStatement(self, stmt: PrintStatement, env: Environment):
        value = self._eval(stmt.value, env)
        print(self._stringify(value))

    def _exec_IfStatement(self, stmt: IfStatement, env: Environment):
        condition = self._eval(stmt.condition, env)
        if self._is_truthy(condition):
            block_env = Environment(parent=env)
            for s in stmt.then_branch:
                self._exec_statement(s, block_env)
        elif stmt.else_branch is not None:
            block_env = Environment(parent=env)
            for s in stmt.else_branch:
                self._exec_statement(s, block_env)

    def _exec_WhileStatement(self, stmt: WhileStatement, env: Environment):
        # Batas iterasi pengaman untuk v0.1 supaya infinite loop tak sengaja
        # tidak membuat prototype hang selamanya di perangkat terbatas (mis. IoT/Termux).
        max_iterations = 10_000_000
        count = 0
        while self._is_truthy(self._eval(stmt.condition, env)):
            block_env = Environment(parent=env)
            for s in stmt.body:
                self._exec_statement(s, block_env)
            count += 1
            if count > max_iterations:
                raise AstraRuntimeError(
                    "Loop melebihi batas maksimum iterasi (kemungkinan infinite loop)",
                    stmt.line,
                )

    def _exec_FunctionDecl(self, stmt: FunctionDecl, env: Environment):
        func = AstraFunction(stmt, closure_env=env)
        env.define(stmt.name, func)

    def _exec_ReturnStatement(self, stmt: ReturnStatement, env: Environment):
        value = None
        if stmt.value is not None:
            value = self._eval(stmt.value, env)
        raise ReturnSignal(value)

    def _exec_ExpressionStatement(self, stmt: ExpressionStatement, env: Environment):
        self._eval(stmt.expr, env)

    # -- expression evaluation ---------------------------------------------------
    def _eval(self, node, env: Environment):
        method_name = f"_eval_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise AstraRuntimeError(
                f"Ekspresi tidak dikenal oleh interpreter: {type(node).__name__}"
            )
        return method(node, env)

    def _eval_LiteralExpr(self, node: LiteralExpr, env: Environment):
        return node.value

    def _eval_VarExpr(self, node: VarExpr, env: Environment):
        return env.get(node.name, node.line)

    def _eval_AssignExpr(self, node: AssignExpr, env: Environment):
        value = self._eval(node.value, env)
        env.set(node.name, value, node.line)
        return value

    def _eval_UnaryExpr(self, node: UnaryExpr, env: Environment):
        operand = self._eval(node.operand, env)
        if node.op == "-":
            self._check_number(operand, node.line, "operator '-' (negasi)")
            return -operand
        if node.op == "not":
            return not self._is_truthy(operand)
        raise AstraRuntimeError(f"Operator unary tidak dikenal: {node.op}", node.line)

    def _eval_BinaryExpr(self, node: BinaryExpr, env: Environment):
        op = node.op

        # short-circuit untuk and/or
        if op == "and":
            left = self._eval(node.left, env)
            if not self._is_truthy(left):
                return left
            return self._eval(node.right, env)
        if op == "or":
            left = self._eval(node.left, env)
            if self._is_truthy(left):
                return left
            return self._eval(node.right, env)

        left = self._eval(node.left, env)
        right = self._eval(node.right, env)

        if op == "+":
            if isinstance(left, str) or isinstance(right, str):
                return self._stringify(left) + self._stringify(right)
            self._check_number(left, node.line, "operator '+'")
            self._check_number(right, node.line, "operator '+'")
            return left + right
        if op == "-":
            self._check_number(left, node.line, "operator '-'")
            self._check_number(right, node.line, "operator '-'")
            return left - right
        if op == "*":
            self._check_number(left, node.line, "operator '*'")
            self._check_number(right, node.line, "operator '*'")
            return left * right
        if op == "/":
            self._check_number(left, node.line, "operator '/'")
            self._check_number(right, node.line, "operator '/'")
            if right == 0:
                raise AstraRuntimeError("Pembagian dengan nol tidak diperbolehkan", node.line)
            result = left / right
            if isinstance(left, int) and isinstance(right, int) and result.is_integer():
                return int(result)
            return result
        if op == "%":
            self._check_number(left, node.line, "operator '%'")
            self._check_number(right, node.line, "operator '%'")
            if right == 0:
                raise AstraRuntimeError("Modulo dengan nol tidak diperbolehkan", node.line)
            return left % right
        if op == "==":
            return left == right
        if op == "!=":
            return left != right
        if op == "<":
            self._check_comparable(left, right, node.line)
            return left < right
        if op == ">":
            self._check_comparable(left, right, node.line)
            return left > right
        if op == "<=":
            self._check_comparable(left, right, node.line)
            return left <= right
        if op == ">=":
            self._check_comparable(left, right, node.line)
            return left >= right

        raise AstraRuntimeError(f"Operator biner tidak dikenal: {op}", node.line)

    def _eval_CallExpr(self, node: CallExpr, env: Environment):
        if not isinstance(node.callee, VarExpr):
            raise AstraRuntimeError("Hanya nama fungsi yang bisa dipanggil di v0.1", node.line)
        callee_name = node.callee.name
        func = env.get(callee_name, node.line)
        args = [self._eval(arg, env) for arg in node.args]

        if isinstance(func, AstraBuiltinFunction):
            if func.arity != -1 and len(args) != func.arity:
                raise AstraRuntimeError(
                    f"Fungsi '{func.name}' membutuhkan {func.arity} argumen, diberikan {len(args)}",
                    node.line,
                )
            return func.py_func(args, node.line)

        if isinstance(func, AstraFunction):
            if len(args) != func.arity:
                raise AstraRuntimeError(
                    f"Fungsi '{func.name}' membutuhkan {func.arity} argumen, diberikan {len(args)}",
                    node.line,
                )
            call_env = Environment(parent=func.closure_env)
            for param_name, arg_value in zip(func.declaration.params, args):
                call_env.define(param_name, arg_value)
            try:
                for s in func.declaration.body:
                    self._exec_statement(s, call_env)
            except ReturnSignal as r:
                return r.value
            return None  # fungsi tanpa return eksplisit

        raise AstraRuntimeError(f"'{callee_name}' bukan fungsi yang bisa dipanggil", node.line)

    # -- helper ----------------------------------------------------------------
    def _is_truthy(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

    def _check_number(self, value, line, context):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise AstraRuntimeError(
                f"Tipe data tidak sesuai untuk {context}: diharapkan angka, dapat '{self._type_name(value)}'",
                line,
            )

    def _check_comparable(self, left, right, line):
        numeric = isinstance(left, (int, float)) and not isinstance(left, bool) and \
                  isinstance(right, (int, float)) and not isinstance(right, bool)
        both_str = isinstance(left, str) and isinstance(right, str)
        if not (numeric or both_str):
            raise AstraRuntimeError(
                f"Tidak bisa membandingkan '{self._type_name(left)}' dengan '{self._type_name(right)}'",
                line,
            )

    def _type_name(self, value):
        if isinstance(value, bool):
            return "boolean"
        if isinstance(value, int):
            return "integer"
        if isinstance(value, float):
            return "float"
        if isinstance(value, str):
            return "string"
        if value is None:
            return "null"
        if isinstance(value, (AstraFunction, AstraBuiltinFunction)):
            return "function"
        return type(value).__name__

    def _stringify(self, value):
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        return str(value)
