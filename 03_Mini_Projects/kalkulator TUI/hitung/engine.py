"""Mesin hitung: tokenizer + parser rekursif-descent, tanpa ketergantungan UI.

Semua logika aritmetika hidup di sini supaya bisa diuji tanpa membuka
terminal. Modul ini tidak boleh mengimpor Textual.

Alur singkat::

    "12 + 3 * (4 - 1)"  ->  tokenize()  ->  _Parser.parse()  ->  21.0
"""

from __future__ import annotations

import math
from dataclasses import dataclass

ANGLE_DEG = "deg"
ANGLE_RAD = "rad"
ANGLES = (ANGLE_DEG, ANGLE_RAD)

MAX_FACTORIAL = 170

_DIV_ZERO = "Pembagian dengan nol tidak terdefinisi"
_TOO_BIG = "Hasil terlalu besar untuk dihitung"

FUNCTIONS = frozenset(
    {
        "sqrt",
        "cbrt",
        "abs",
        "sin",
        "cos",
        "tan",
        "asin",
        "acos",
        "atan",
        "log",
        "log10",
        "logn",
        "ln",
        "exp",
        "floor",
        "ceil",
        "round",
        "ncr",
        "npr",
    }
)

CONSTANTS = {
    "pi": math.pi,
    "e": math.e,
    "tau": math.tau,
}

_NUMBER_START = frozenset("0123456789.,")
_NAME_START = frozenset("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_")
_SIMPLE_OPS = frozenset("+-*/^%!();")


class CalcError(ValueError):
    """Kesalahan ekspresi dengan pesan yang siap ditampilkan ke pengguna."""


@dataclass(frozen=True, slots=True)
class Token:
    """Satu potongan ekspresi: angka, nama, atau operator."""

    kind: str
    text: str
    value: float = 0.0


def tokenize(expression: str) -> list[Token]:
    """Pecah ekspresi menjadi token. Spasi diabaikan."""
    tokens: list[Token] = []
    index = 0
    length = len(expression)

    while index < length:
        char = expression[index]

        if char.isspace():
            index += 1
            continue

        if char in _NUMBER_START:
            text, value, index = _read_number(expression, index)
            tokens.append(Token("number", text, value))
            continue

        if char in _NAME_START:
            start = index
            while index < length and (
                expression[index].isalnum() or expression[index] == "_"
            ):
                index += 1
            tokens.append(Token("name", expression[start:index].lower()))
            continue

        if char in _SIMPLE_OPS:
            tokens.append(Token("op", char))
            index += 1
            continue

        raise CalcError(f"Karakter tidak dikenal: '{char}'")

    return tokens


def _read_number(expression: str, start: int) -> tuple[str, float, int]:
    """Baca satu angka. Titik dan koma sama-sama boleh jadi desimal."""
    index = start
    length = len(expression)
    parts: list[str] = []
    has_separator = False

    while index < length:
        char = expression[index]
        if char.isdigit():
            parts.append(char)
            index += 1
        elif char in ".," and not has_separator:
            has_separator = True
            parts.append(".")
            index += 1
        else:
            break

    text = "".join(parts)
    if text in {"", "."}:
        raise CalcError(f"Angka tidak valid di posisi {start + 1}")
    try:
        value = float(text)
    except ValueError:
        raise CalcError(f"Angka tidak valid: '{text}'") from None
    return text, value, index


class _Parser:
    """Parser rekursif-descent dengan prioritas operator biasa."""

    def __init__(
        self,
        tokens: list[Token],
        *,
        angle: str,
        variables: dict[str, float],
    ) -> None:
        self.tokens = tokens
        self.angle = angle
        self.variables = variables
        self.index = 0

    # ----------------------------------------------------------- token util
    def _peek(self) -> Token | None:
        if self.index < len(self.tokens):
            return self.tokens[self.index]
        return None

    def _advance(self) -> Token:
        token = self.tokens[self.index]
        self.index += 1
        return token

    # --------------------------------------------------------------- grammar
    def parse(self) -> float:
        if not self.tokens:
            raise CalcError("Ekspresi masih kosong")

        value = self._expression()
        leftover = self._peek()
        if leftover is not None:
            if leftover.kind == "op" and leftover.text == ")":
                raise CalcError("Tanda kurung tutup ')' tanpa pasangan")
            raise CalcError(f"Ada bagian yang tidak terbaca: '{leftover.text}'")
        return _checked(value)

    def _expression(self) -> float:
        value = self._term()
        while True:
            token = self._peek()
            if token is None or token.kind != "op" or token.text not in "+-":
                return value
            self._advance()
            if token.text == "+":
                value += self._term()
            else:
                value -= self._term()

    def _term(self) -> float:
        value = self._unary()
        while True:
            token = self._peek()
            if token is None or token.kind != "op" or token.text not in "*/":
                return value
            self._advance()
            right = self._unary()
            if token.text == "*":
                value *= right
            else:
                if right == 0:
                    raise CalcError(_DIV_ZERO)
                value /= right

    def _unary(self) -> float:
        token = self._peek()
        if token is not None and token.kind == "op" and token.text in "+-":
            self._advance()
            value = self._unary()
            return -value if token.text == "-" else value
        return self._power()

    def _power(self) -> float:
        base = self._postfix()
        token = self._peek()
        if token is not None and token.kind == "op" and token.text == "^":
            self._advance()
            exponent = self._unary()
            return _power(base, exponent)
        return base

    def _postfix(self) -> float:
        value = self._primary()
        while True:
            token = self._peek()
            if token is None or token.kind != "op":
                return value
            if token.text == "%":
                self._advance()
                value = value / 100.0
            elif token.text == "!":
                self._advance()
                value = _factorial(value)
            else:
                return value

    def _primary(self) -> float:
        token = self._peek()
        if token is None:
            raise CalcError("Ekspresi belum lengkap")
        if token.kind == "number":
            self._advance()
            return token.value
        if token.kind == "name":
            self._advance()
            return self._name(token.text)
        if token.kind == "op" and token.text == "(":
            self._advance()
            inner = self._peek()
            if inner is None:
                raise CalcError("Kurung buka '(' belum ditutup")
            if inner.kind == "op" and inner.text == ")":
                raise CalcError("Tanda kurung kosong '()'")
            value = self._expression()
            closing = self._peek()
            if closing is None or closing.kind != "op" or closing.text != ")":
                raise CalcError("Kurung tutup ')' kurang")
            self._advance()
            return value
        raise CalcError(f"Tanda '{token.text}' tidak bisa dipakai di posisi ini")

    def _name(self, name: str) -> float:
        if name in FUNCTIONS:
            token = self._peek()
            if token is None or token.kind != "op" or token.text != "(":
                raise CalcError(f"Fungsi '{name}' butuh argumen, mis. {name}(9)")
            self._advance()
            inner = self._peek()
            if inner is None or (inner.kind == "op" and inner.text == ")"):
                raise CalcError(f"Fungsi '{name}' butuh angka di dalam kurung")
            args = [self._expression()]
            while True:
                sep = self._peek()
                if sep is None or sep.kind != "op" or sep.text != ";":
                    break
                self._advance()
                args.append(self._expression())
            closing = self._peek()
            if closing is None or closing.kind != "op" or closing.text != ")":
                raise CalcError("Kurung tutup ')' kurang")
            self._advance()
            return self._call(name, args)
        if name in self.variables:
            return self.variables[name]
        if name in CONSTANTS:
            return CONSTANTS[name]
        raise CalcError(f"Nama tidak dikenal: '{name}'")

    # ------------------------------------------------------------- functions
    def _call(self, name: str, args: list[float]) -> float:
        if name in {"ncr", "npr", "logn"}:
            if len(args) != 2:
                raise CalcError(f"Fungsi '{name}' butuh 2 argumen, mis. {name}(5;2)")
            a, b = args
            if name == "ncr":
                return _ncr(a, b)
            if name == "npr":
                return _npr(a, b)
            if b <= 0 or a <= 0 or a == 1:
                raise CalcError("logn butuh basis > 0, basis != 1, dan nilai > 0")
            return math.log(b, a)

        if len(args) != 1:
            raise CalcError(f"Fungsi '{name}' butuh 1 argumen")
        argument = args[0]

        if name == "sqrt":
            if argument < 0:
                raise CalcError("Akar kuadrat butuh nilai >= 0")
            return math.sqrt(argument)
        if name == "cbrt":
            return math.copysign(abs(argument) ** (1.0 / 3.0), argument)
        if name == "abs":
            return abs(argument)
        if name in {"sin", "cos", "tan"}:
            radians = self._to_radians(argument)
            if name == "sin":
                return math.sin(radians)
            if name == "cos":
                return math.cos(radians)
            if abs(math.cos(radians)) < 1e-12:
                raise CalcError("tan tidak terdefinisi pada sudut ini")
            return math.tan(radians)
        if name in {"asin", "acos"}:
            if not -1 <= argument <= 1:
                raise CalcError(f"{name} butuh nilai antara -1 dan 1")
            radians = math.asin(argument) if name == "asin" else math.acos(argument)
            return self._from_radians(radians)
        if name == "atan":
            return self._from_radians(math.atan(argument))
        if name in {"log", "log10"}:
            if argument <= 0:
                raise CalcError("log butuh nilai > 0")
            return math.log10(argument)
        if name == "ln":
            if argument <= 0:
                raise CalcError("ln butuh nilai > 0")
            return math.log(argument)
        if name == "exp":
            try:
                result = math.exp(argument)
            except OverflowError:
                raise CalcError(_TOO_BIG) from None
            return result
        if name == "floor":
            return math.floor(argument)
        if name == "ceil":
            return math.ceil(argument)
        if name == "round":
            return _round_half_up(argument)
        raise CalcError(f"Fungsi tidak dikenal: '{name}'")

    def _to_radians(self, value: float) -> float:
        if self.angle == ANGLE_DEG:
            return math.radians(value)
        return value

    def _from_radians(self, value: float) -> float:
        if self.angle == ANGLE_DEG:
            return math.degrees(value)
        return value


def _checked(value: float) -> float:
    """Pastikan hasil berupa bilangan real yang masih bisa ditampilkan."""
    result = float(value)
    if not math.isfinite(result):
        raise CalcError(_TOO_BIG)
    return result


def _power(base: float, exponent: float) -> float:
    try:
        result = base**exponent
    except ZeroDivisionError:
        raise CalcError("Pangkat negatif dari nol tidak terdefinisi") from None
    except OverflowError:
        raise CalcError(_TOO_BIG) from None
    except ValueError:
        raise CalcError("Pangkat tidak valid untuk angka ini") from None
    if isinstance(result, complex):
        raise CalcError("Hasil bukan bilangan real")
    return _checked(result)


def _factorial(value: float) -> float:
    if value < 0 or abs(value - round(value)) > 1e-9:
        raise CalcError("Faktorial hanya untuk bilangan bulat >= 0")
    number = int(round(value))
    if number > MAX_FACTORIAL:
        raise CalcError(f"Faktorial maksimal {MAX_FACTORIAL}!")
    return float(math.factorial(number))


def _round_half_up(value: float) -> float:
    if value >= 0:
        return float(math.floor(value + 0.5))
    return float(math.ceil(value - 0.5))


def _whole_number(value: float, *, label: str) -> int:
    if abs(value - round(value)) > 1e-9:
        raise CalcError(f"{label} butuh bilangan bulat")
    return int(round(value))


def _ncr(n_value: float, r_value: float) -> float:
    n = _whole_number(n_value, label="nCr: n")
    r = _whole_number(r_value, label="nCr: r")
    if n < 0 or r < 0 or r > n:
        raise CalcError("nCr butuh n,r bulat dengan 0 <= r <= n")
    return float(math.comb(n, r))


def _npr(n_value: float, r_value: float) -> float:
    n = _whole_number(n_value, label="nPr: n")
    r = _whole_number(r_value, label="nPr: r")
    if n < 0 or r < 0 or r > n:
        raise CalcError("nPr butuh n,r bulat dengan 0 <= r <= n")
    return float(math.perm(n, r))


def evaluate(
    expression: str,
    *,
    angle: str = ANGLE_DEG,
    ans: float = 0.0,
) -> float:
    """Hitung ekspresi dan kembalikan hasilnya.

    ``angle`` menentukan satuan sudut untuk fungsi trigonometri, ``ans``
    menjadi nilai variabel ``ans`` (hasil perhitungan sebelumnya).
    """
    if angle not in ANGLES:
        raise ValueError(f"mode sudut tidak dikenal: {angle}")
    tokens = tokenize(expression)
    variables = {"ans": float(ans)}
    return _Parser(tokens, angle=angle, variables=variables).parse()


def try_evaluate(
    expression: str,
    *,
    angle: str = ANGLE_DEG,
    ans: float = 0.0,
) -> tuple[float | None, str | None]:
    """Versi ``evaluate`` yang tidak melempar: (nilai, pesan_error)."""
    try:
        return evaluate(expression, angle=angle, ans=ans), None
    except CalcError as error:
        return None, str(error)
