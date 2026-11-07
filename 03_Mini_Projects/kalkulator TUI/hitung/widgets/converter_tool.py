"""Konverter unit berbasis tombol."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from ..data.units import CategoryDef, get_category, list_categories
from ..engines.conversion_engine import ConversionError, convert_value
from ..format import format_number
from ..history import HistoryRecord
from .converter_tabs import ConverterTabs
from .numeric_keypad import NumericKey, NumericKeypad
from .unit_selector import UnitSelector


def _plain(value: float) -> str:
    return format(Decimal(repr(value)).normalize(), "f")


class ConverterTool(Vertical):
    DEFAULT_CSS = """
    ConverterTool { height: 1fr; layout: vertical; padding: 0 1; }
    """

    def __init__(self, *, id: str | None = None) -> None:
        super().__init__(id=id)
        self._categories = list_categories()
        self._cat: CategoryDef = self._categories[0]
        self._texts = {"from": "0", "to": ""}

    @property
    def host(self):
        return self.app

    def compose(self) -> ComposeResult:
        categories = [(category.title, category.category_id) for category in self._categories]
        units = [(unit.label, unit.unit_id) for unit in self._cat.units]
        yield ConverterTabs(categories, id="conv-tabs")
        with Horizontal(id="conv-panels"):
            source = UnitSelector(
                "DARI",
                select_id="conv-from-unit",
                value_id="conv-from-value",
                options=units,
                id="conv-from",
            )
            yield source
            yield Button("⇄", id="conv-swap", tooltip="Tukar satuan")
            target = UnitSelector(
                "KE",
                select_id="conv-to-unit",
                value_id="conv-to-value",
                options=units,
                default_index=1,
                id="conv-to",
            )
            yield target
        yield Static("", id="conv-result")
        yield NumericKeypad(prefix="conv-", id="conv-keypad")

    def on_mount(self) -> None:
        self._refresh_values()
        self._sync_responsive()

    def on_resize(self, event) -> None:
        self._sync_responsive()

    def _sync_responsive(self) -> None:
        try:
            panels = self.query_one("#conv-panels")
        except Exception:
            return
        # Susun vertikal pada lebar sempit agar FROM/TO tidak bertabrakan.
        narrow = self.size.width < 72
        panels.styles.layout = "vertical" if narrow else "horizontal"
        try:
            swap = self.query_one("#conv-swap", Button)
            swap.styles.margin = (0, 0, 1, 0) if narrow else (2, 1, 0, 1)
            swap.styles.width = "100%" if narrow else 7
        except Exception:
            pass

    def focus_default(self) -> None:
        self.query_one("#conv-from", UnitSelector).focus()

    def _fmt(self, value: float) -> str:
        settings = self.host.settings
        return format_number(
            value,
            precision=settings.precision,
            thousands=settings.thousands,
            number_format=getattr(settings, "number_format", "id"),
        )

    def _parse(self, text: str) -> float | None:
        raw = text.strip().replace(",", ".")
        try:
            return float(raw)
        except ValueError:
            return None

    def _focused_side(self) -> str:
        target = self.query_one("#conv-to", UnitSelector)
        try:
            focused = self.app.focused
            if target.has_focus or (focused is not None and focused in target.query("*")):
                return "to"
        except Exception:
            pass
        return "from"

    def _focus_side(self, side: str) -> None:
        self.query_one(f"#conv-{side}", UnitSelector).focus()

    def _units(self) -> tuple[str, str]:
        source = self.query_one("#conv-from", UnitSelector).value
        target = self.query_one("#conv-to", UnitSelector).value
        return source, target

    def _refresh_values(self) -> None:
        from_panel = self.query_one("#conv-from", UnitSelector)
        to_panel = self.query_one("#conv-to", UnitSelector)
        result = self.query_one("#conv-result", Static)
        value = self._parse(self._texts["from"])
        if value is None:
            from_panel.show_value(self._texts["from"] or "0")
            to_panel.show_value("")
            result.update("Nilai tidak valid. Contoh: 12,5")
            return
        source, target = self._units()
        try:
            out = convert_value(value, source, target, self._cat.category_id)
        except ConversionError as error:
            result.update(str(error))
            return
        self._texts["to"] = _plain(out)
        from_panel.show_value(self._fmt(value))
        to_panel.show_value(self._fmt(out))
        result.update(f"{self._fmt(value)} {source} = {self._fmt(out)} {target}")

    def _apply_category(self, category: CategoryDef) -> None:
        self._cat = category
        units = [(unit.label, unit.unit_id) for unit in category.units]
        source = self.query_one("#conv-from", UnitSelector)
        target = self.query_one("#conv-to", UnitSelector)
        source.set_options(units)
        target.set_options(units)
        if len(units) > 1:
            target.select_unit(units[1][1])
        self._texts = {"from": "0", "to": ""}
        self._refresh_values()

    def on_converter_tabs_category_changed(
        self, event: ConverterTabs.CategoryChanged
    ) -> None:
        event.stop()
        category = get_category(event.category_id)
        if category is not None:
            self._apply_category(category)

    def on_unit_selector_unit_changed(self, event: UnitSelector.UnitChanged) -> None:
        event.stop()
        self._refresh_values()

    def on_numeric_key(self, event: NumericKey) -> None:
        event.stop()
        key = event.key
        if key == "key-up":
            self._focus_side("from")
            return
        if key == "key-down":
            self._focus_side("to")
            return
        if key == "key-equals":
            self._save_history()
            self.host.notify("Konversi disimpan ke riwayat.", timeout=2)
            return

        side = self._focused_side()
        text = self._texts[side]
        if key == "key-clear":
            text = ""
        elif key == "key-backspace":
            text = text[:-1]
        elif key == "key-sign":
            text = text[1:] if text.startswith("-") else "-" + text
        else:
            insert = self.query_one(NumericKeypad).insert_texts.get(key)
            if not insert:
                return
            if insert == "." and "." in text:
                return
            if text == "0" and insert != ".":
                text = insert
            else:
                text += insert
        self._texts[side] = text
        if side == "to":
            self._rebuild_from()
        self._refresh_values()

    def _rebuild_from(self) -> None:
        value = self._parse(self._texts["to"])
        if value is None:
            return
        source, target = self._units()
        try:
            back = convert_value(value, target, source, self._cat.category_id)
        except ConversionError:
            return
        self._texts["from"] = _plain(back)

    def _save_history(self) -> None:
        value = self._parse(self._texts["from"])
        if value is None:
            return
        source, target = self._units()
        try:
            out = convert_value(value, source, target, self._cat.category_id)
        except ConversionError:
            return
        record = HistoryRecord(
            at=datetime.now().astimezone(),
            expression=f"{_plain(value)} {source} -> {target} [{self._cat.category_id}]",
            result=self._fmt(out),
            value=out,
            category=f"converter:{self._cat.category_id}",
            input_text=_plain(value),
            output_text=self._fmt(out),
        )
        try:
            self.host.storage.append_history(record)
        except OSError as error:
            self.app.log.error(f"Gagal menyimpan riwayat: {error}")
            return
        self.host.records.append(record)
        self.host.refresh_dashboard_recent()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id != "conv-swap":
            return
        event.stop()
        source = self.query_one("#conv-from", UnitSelector)
        target = self.query_one("#conv-to", UnitSelector)
        source_unit, target_unit = source.value, target.value
        source.select_unit(target_unit)
        target.select_unit(source_unit)
        self._texts["from"], self._texts["to"] = (
            self._texts["to"] or "0",
            self._texts["from"],
        )
        self._refresh_values()
