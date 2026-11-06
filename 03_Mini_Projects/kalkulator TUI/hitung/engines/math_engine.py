"""Mesin matematika & statistik (murni)."""

from __future__ import annotations

import math
import statistics

from .util import EngineError, to_float, to_int


def gcd(a: int, b: int) -> int:
    x, y = to_int(a, "a"), to_int(b, "b")
    return math.gcd(x, y)


def lcm(a: int, b: int) -> int:
    x, y = to_int(a, "a"), to_int(b, "b")
    if x == 0 or y == 0:
        return 0
    return abs(x * y) // math.gcd(x, y)


def is_prime(n: int) -> bool:
    x = to_int(n, "n")
    if x < 2:
        return False
    if x % 2 == 0:
        return x == 2
    r = int(math.isqrt(x))
    f = 3
    while f <= r:
        if x % f == 0:
            return False
        f += 2
    return True


def prime_factors(n: int) -> list[int]:
    x = to_int(n, "n")
    if x < 2:
        raise EngineError("Faktorisasi prima butuh bilangan bulat >= 2.")
    factors: list[int] = []
    d = 2
    while d * d <= x:
        while x % d == 0:
            factors.append(d)
            x //= d
        d = 3 if d == 2 else d + 2
    if x > 1:
        factors.append(x)
    return factors


def stats(values: list[float]) -> dict[str, float | None]:
    nums = [to_float(v, "data") for v in values]
    if not nums:
        raise EngineError("Data statistik tidak boleh kosong.")
    out: dict[str, float | None] = {
        "mean": statistics.fmean(nums),
        "median": statistics.median(nums),
        "count": float(len(nums)),
        "min": min(nums),
        "max": max(nums),
    }
    try:
        out["mode"] = statistics.mode(nums)
    except statistics.StatisticsError:
        out["mode"] = None
    out["stdev"] = statistics.stdev(nums) if len(nums) > 1 else 0.0
    return out


def permutations(n: int, r: int) -> int:
    return math.perm(to_int(n, "n"), to_int(r, "r"))


def combinations(n: int, r: int) -> int:
    return math.comb(to_int(n, "n"), to_int(r, "r"))
