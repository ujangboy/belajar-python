"""Utilitas teks kecil untuk tampilan."""

from __future__ import annotations

ELLIPSIS = "…"


def shorten(text: str, limit: int) -> str:
    """Potong teks agar muat di lebar sempit, akhiri dengan elipsis."""
    if limit <= 0:
        return ""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)] + ELLIPSIS
