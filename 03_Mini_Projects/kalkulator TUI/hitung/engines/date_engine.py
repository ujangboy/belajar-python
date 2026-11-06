"""Mesin tanggal & waktu (murni)."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone

from .util import EngineError, to_int


def parse_date(text: str) -> date:
    raw = text.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).date()
        except ValueError:
            pass
    raise EngineError("Format tanggal tidak valid. Gunakan YYYY-MM-DD atau DD/MM/YYYY.")


def date_diff(a: str, b: str) -> dict[str, int]:
    d1, d2 = parse_date(a), parse_date(b)
    delta = abs((d2 - d1).days)
    return {"days": delta, "weeks": delta // 7, "remaining_days": delta % 7}


def add_days(start: str, days: int) -> date:
    d = parse_date(start)
    return d + timedelta(days=to_int(days, "hari"))


def age(birth: str, on: str | None = None) -> dict[str, int]:
    b = parse_date(birth)
    ref = parse_date(on) if on else date.today()
    if ref < b:
        raise EngineError("Tanggal acuan sebelum tanggal lahir.")
    years = ref.year - b.year - ((ref.month, ref.day) < (b.month, b.day))
    # months/days approx via anniversary
    anniv_year = b.year + years
    try:
        anniv = b.replace(year=anniv_year)
    except ValueError:
        anniv = b.replace(year=anniv_year, day=28)
    months = (ref.year - anniv.year) * 12 + (ref.month - anniv.month)
    if ref.day < anniv.day:
        months -= 1
    month_anniv_month = anniv.month + months
    month_anniv_year = anniv.year + (month_anniv_month - 1) // 12
    month_anniv_month = (month_anniv_month - 1) % 12 + 1
    try:
        month_anniv = date(month_anniv_year, month_anniv_month, b.day)
    except ValueError:
        month_anniv = date(month_anniv_year, month_anniv_month, 28)
    days = (ref - month_anniv).days
    if months < 0:
        months = 0
    if days < 0:
        days = 0
    return {"years": years, "months": months, "days": days, "total_days": (ref - b).days}


def from_unix(ts: int) -> datetime:
    return datetime.fromtimestamp(to_int(ts, "timestamp"), tz=timezone.utc)


def to_unix(dt_text: str) -> int:
    raw = dt_text.strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(raw, fmt)
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            pass
    raise EngineError("Format datetime tidak valid. Gunakan YYYY-MM-DD atau YYYY-MM-DD HH:MM[:SS].")
