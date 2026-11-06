from __future__ import annotations

import math

import pytest

from hitung.engine import CalcError, evaluate, tokenize, try_evaluate


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("1+1", 2.0),
        ("2+3*4", 14.0),
        ("(2+3)*4", 20.0),
        ("10-4-3", 3.0),
        ("100/4/5", 5.0),
        ("2^3^2", 512.0),
        ("-2^2", -4.0),
        ("2^-3", 0.125),
        ("--3", 3.0),
        ("+5", 5.0),
        ("200*10%", 20.0),
        ("50%", 0.5),
        ("5!", 120.0),
        ("0!", 1.0),
        ("3!!", 720.0),
        ("1,5+2", 3.5),
        (".5*2", 1.0),
        ("3.*3", 9.0),
        ("pi", math.pi),
        ("e", math.e),
        ("tau", math.tau),
        ("  12   +   3  ", 15.0),
    ],
)
def test_evaluate_expressions(expression: str, expected: float) -> None:
    assert evaluate(expression) == pytest.approx(expected)


def test_ans_variable() -> None:
    assert evaluate("ans * 2", ans=7.0) == pytest.approx(14.0)


def test_ans_defaults_to_zero() -> None:
    assert evaluate("ans + 1") == pytest.approx(1.0)


def test_functions() -> None:
    assert evaluate("sqrt(144)") == pytest.approx(12.0)
    assert evaluate("cbrt(27)") == pytest.approx(3.0)
    assert evaluate("cbrt(-8)") == pytest.approx(-2.0)
    assert evaluate("abs(-3.5)") == pytest.approx(3.5)
    assert evaluate("floor(2.9)") == 2.0
    assert evaluate("ceil(2.1)") == 3.0
    assert evaluate("round(2.5)") == 3.0
    assert evaluate("round(-2.5)") == -3.0
    assert evaluate("log(1000)") == pytest.approx(3.0)
    assert evaluate("log10(100)") == pytest.approx(2.0)
    assert evaluate("logn(2;8)") == pytest.approx(3.0)
    assert evaluate("ln(e)") == pytest.approx(1.0)
    assert evaluate("exp(0)") == pytest.approx(1.0)
    assert evaluate("ncr(5;2)") == 10.0
    assert evaluate("npr(5;2)") == 20.0


def test_trigonometry_degree_mode() -> None:
    assert evaluate("sin(30)") == pytest.approx(0.5)
    assert evaluate("cos(60)") == pytest.approx(0.5)
    assert evaluate("asin(0.5)") == pytest.approx(30.0)


def test_trigonometry_radian_mode() -> None:
    assert evaluate("sin(pi/2)", angle="rad") == pytest.approx(1.0)
    assert evaluate("acos(0)", angle="rad") == pytest.approx(math.pi / 2)


def test_unknown_angle_mode_fails() -> None:
    with pytest.raises(ValueError):
        evaluate("1+1", angle="gon")


@pytest.mark.parametrize(
    ("expression", "message"),
    [
        ("", "masih kosong"),
        ("   ", "masih kosong"),
        ("2+", "belum lengkap"),
        ("*2", "tidak bisa dipakai"),
        ("(1+2", "kurang"),
        ("1+2)", "tanpa pasangan"),
        ("()", "kosong"),
        ("1/0", "pembagian dengan nol"),
        ("sqrt(-1)", ">= 0"),
        ("log(0)", "> 0"),
        ("ln(0)", "> 0"),
        ("tan(90)", "tidak terdefinisi"),
        ("asin(2)", "antara -1 dan 1"),
        ("foo(1)", "tidak dikenal"),
        ("2@3", "karakter tidak dikenal"),
        ("(-1)!", "faktorial"),
        ("2,5!", "faktorial"),
        ("173!", "faktorial maksimal"),
        ("9^999", "terlalu besar"),
        ("0^-1", "pangkat negatif dari nol"),
        ("ncr(5)", "2 argumen"),
        ("ncr(5;6)", "ncr butuh"),
        ("npr(2;3)", "npr butuh"),
        ("logn(1;8)", "logn butuh"),
    ],
)
def test_errors(expression: str, message: str) -> None:
    with pytest.raises(CalcError) as info:
        evaluate(expression)
    assert message in str(info.value).lower()


def test_tokenize() -> None:
    tokens = tokenize(" 12 + 3,5 ")
    assert [token.kind for token in tokens] == ["number", "op", "number"]
    assert tokens[0].value == 12.0
    assert tokens[2].value == 3.5


def test_try_evaluate_success() -> None:
    assert try_evaluate("2*3") == (6.0, None)


def test_try_evaluate_error() -> None:
    value, error = try_evaluate("1/0")
    assert value is None
    assert error is not None
    assert "nol" in error.lower()
