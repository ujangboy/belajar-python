# KALKULATOR PRO v2.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild HITUNG into KALKULATOR PRO, a button-based scientific calculator and 9-category unit converter with modern dark-navy TUI, preserving the safe expression engine and JSONL storage.

**Architecture:** Keep the pure domain modules (`engine.py`, `format.py`, `history.py`, `config.py`, `storage.py`) unchanged. Replace the UI layer: sidebar navigation, read-only calculator display, scientific keypad, converter tabs + numeric keypad, dashboard, percentage and tip screens. Delete finance/electrical/math/date/data tools.

**Tech Stack:** Python 3.11+, Textual 8.x (only runtime dependency), Rich (bundled with Textual), pytest.

**Spec:** `docs/superpowers/specs/2026-11-06-kalkulator-pro-design.md`

## Global Constraints

- Python 3.11+, Textual `>=8.2,<9.0`, single runtime dependency `textual`.
- No `eval`/`exec` for user input; all calculations through `hitung/engine.py` or `hitung/engines/*`.
- Brand text: **KALKULATOR PRO** (replace HITUNG/Calculator Pro).
- Storage: `config.json` + `history.jsonl` (JSONL), no SQLite.
- UI messages in Bahasa Indonesia.
- Minimum terminal 60×18; layout must adapt 60–140 columns.
- All buttons must have an event handler; no decorative buttons.
- Design colors (design §8): background `#0B0E14`, main panel `#111827`, secondary `#1A202B`, border `#2A3444`, text `#E6EDF3`, muted `#93A1B3`, accent `#4C8DFF`, result `#6FD3A8`, clear `#FF7A6B`.

## Review Focus

- Contextual percent: `200 + 10%` must equal `220`, not `200.1`. Test in standard keypad.
- Unit conversion accuracy for new units (Rankine, nautical mile, stone, imperial gallon, square mile, ft/s, IEC data). Test in `test_conversions.py`.
- Converter focus navigation: `↑` focuses FROM, `↓` focuses TO; numeric keypad edits the focused field. Test in converter tool.
- Responsive layout at 60×18: sidebar hidden, keypad compressed, no clipped buttons. Test in `test_app.py`.
- History persistence across restart with category labels (`standard`, `scientific`, `converter:<cat>`, `percentage`, `tip`). Test in `test_app.py` / `test_history.py`.

---

### Task 1: Theme & Branding

**Files:**
- Modify: `hitung/theme.py`
- Modify: `hitung/hitung.tcss`
- Modify: `hitung/widgets/topbar.py`
- Test: `tests/test_theme.py`

**Interfaces:**
- Produces: `build_theme(*, mode: str = "dark", accent: str = "blue") -> Theme` with design §8 colors. `ACCENTS` dict maps `blue`→`#4C8DFF`, `mint`→`#6FD3A8`, `amber`→`#FF7A6B`, `rose`→`#F28FAD`.
- Produces: `topbar.py` brand `KALKULATOR PRO`, subtitle `Smart Calculation in Your Terminal`.

- [ ] **Step 1:** Write failing test in `tests/test_theme.py`:

```python
from hitung.theme import build_theme, ACCENTS

def test_dark_theme_colors():
    theme = build_theme(mode="dark", accent="blue")
    assert theme.background == "#0B0E14"
    assert theme.surface == "#111827"
    assert theme.panel == "#1A202B"
    assert theme.primary == "#4C8DFF"
    assert theme.variables["border"] == "#2A3444"
    assert theme.variables["muted"] == "#93A1B3"

def test_accents():
    assert ACCENTS["blue"] == "#4C8DFF"
    assert ACCENTS["mint"] == "#6FD3A8"
    assert ACCENTS["amber"] == "#FF7A6B"
```

- [ ] **Step 2:** Run `pytest tests/test_theme.py -v` (fails: colors wrong).
- [ ] **Step 3:** Update `hitung/theme.py`: change `ACCENTS` and `build_theme` colors to design §8; default accent `blue`.
- [ ] **Step 4:** Run `pytest tests/test_theme.py -v` (passes).
- [ ] **Step 5:** Update `hitung/hitung.tcss`: replace old palette with design §8; add `border: round` to buttons, panels; style sidebar, display, keypad.
- [ ] **Step 6:** Update `hitung/widgets/topbar.py`: brand `KALKULATOR PRO`, subtitle `Smart Calculation in Your Terminal`.
- [ ] **Step 7:** Run `pytest -q` (all existing tests still pass; visual change only).
- [ ] **Step 8:** Commit: `feat: modern dark-navy theme and KALKULATOR PRO branding`.

---

### Task 2: Navigation Registry

**Files:**
- Modify: `hitung/navigation.py`
- Test: `tests/test_navigation.py`

**Interfaces:**
- Produces: `default_tools() -> list[ToolSpec]` with exactly these `tool_id`s in order: `dashboard`, `standard`, `scientific`, `converter`, `percentage`, `tip`, `history`, `favorites`, `settings`, `help`.
- `ToolSpec` fields unchanged.

- [ ] **Step 1:** Write failing test `tests/test_navigation.py`:

```python
from hitung.navigation import default_tools

def test_tool_ids():
    ids = [t.tool_id for t in default_tools()]
    assert ids == ["dashboard","standard","scientific","converter","percentage","tip","history","favorites","settings","help"]

def test_shortcuts():
    by_id = {t.tool_id: t for t in default_tools()}
    assert by_id["standard"].shortcut == "Ctrl+1"
    assert by_id["scientific"].shortcut == "Ctrl+2"
    assert by_id["converter"].shortcut == "Ctrl+3"
```

- [ ] **Step 2:** Run `pytest tests/test_navigation.py -v` (fails).
- [ ] **Step 3:** Rewrite `default_tools()` in `hitung/navigation.py` with the 10 tools above, categories `Sistem`, `Kalkulator`, `Konverter`, `Sehari-hari`, `Bantuan`.
- [ ] **Step 4:** Run `pytest tests/test_navigation.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: update tool registry for KALKULATOR PRO`.

---

### Task 3: Core Widgets (Sidebar, Display, Keypad)

**Files:**
- Create: `hitung/widgets/sidebar.py`
- Create: `hitung/widgets/display.py`
- Create: `hitung/widgets/keypad.py`
- Test: `tests/test_core_widgets.py`

**Interfaces:**
- `Sidebar(Vertical)`: `compose()` yields `Button` with ids `side-<tool_id>`; `on_button_pressed` calls `self.app.open_tool(tool_id)`.
- `CalculatorDisplay(Vertical)`: methods `set_expression(text: str)`, `set_result(text: str, preview: bool = False)`, `set_status(text: str, error: bool = False)`, `set_angle(mode: str)`. Children ids: `#calc-expression`, `#calc-result`, `#calc-status`, `#calc-angle`.
- `ScientificKeypad(Vertical)`: class attr `KEYS: tuple[tuple[str, str, str], ...]` of `(button_id, label, insert_text)`. Emits `KeyPressed` message with `key: str`. Standard subset and full scientific set defined as module constants `STANDARD_KEYS`, `SCIENTIFIC_KEYS`.

- [ ] **Step 1:** Write failing tests in `tests/test_core_widgets.py` (use `run_test` and `pilot.click`):

```python
import pytest
from hitung.app import HitungApp
from hitung.widgets.display import CalculatorDisplay
from hitung.widgets.keypad import ScientificKeypad, STANDARD_KEYS, SCIENTIFIC_KEYS

async def test_sidebar_opens_tool(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        await pilot.click("#side-scientific")
        await pilot.pause()
        assert app._active_tool == "scientific"

async def test_display_updates(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        display = app.query_one(CalculatorDisplay)
        display.set_expression("12 + 3")
        display.set_result("15", preview=True)
        display.set_status("OK")
        display.set_angle("rad")
        assert display.query_one("#calc-expression").content == "12 + 3"
        assert "-preview" in display.query_one("#calc-result").classes

def test_keypad_layouts():
    assert len(STANDARD_KEYS) == 24
    assert len(SCIENTIFIC_KEYS) == 35
    ids = [k[0] for k in SCIENTIFIC_KEYS]
    assert "key-equals" in ids and "key-clear" in ids and "key-swap" in ids
```

- [ ] **Step 2:** Run `pytest tests/test_core_widgets.py -v` (fails: modules missing).
- [ ] **Step 3:** Implement `hitung/widgets/sidebar.py`, `hitung/widgets/display.py`, `hitung/widgets/keypad.py` per interfaces. Use `Message` from `textual.message` for `KeyPressed`.
- [ ] **Step 4:** Run `pytest tests/test_core_widgets.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: add sidebar, calculator display, and scientific keypad widgets`.

---

### Task 4: Standard Calculator (button-based)

**Files:**
- Rewrite: `hitung/widgets/standard_tool.py`
- Test: `tests/test_standard_tool.py`

**Interfaces:**
- Consumes: `CalculatorDisplay`, `ScientificKeypad` with `STANDARD_KEYS`, `hitung.engine.evaluate`, `hitung.format.format_number`, `hitung.history.HistoryRecord`.
- Produces: `StandardTool(Vertical)` with `compose()` yielding `CalculatorDisplay` + `ScientificKeypad(STANDARD_KEYS)`; handles `on_key_pressed`; state `expression: str`, `last_result: float | None`.

- [ ] **Step 1:** Write failing tests in `tests/test_standard_tool.py`:

```python
import pytest
from hitung.app import HitungApp

async def test_button_input_and_result(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in ["key-1","key-plus","key-2","key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        display = app.query_one("#calc-result")
        assert display.content == "3"
        assert len(app.records) == 1

async def test_contextual_percent(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in ["key-2","key-0","key-0","key-plus","key-1","key-0","key-percent","key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert app.query_one("#calc-result").content == "220"

async def test_clear_and_backspace(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        for key in ["key-1","key-2","key-backspace"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert app.query_one("#calc-expression").content == "1"
        await pilot.click("#key-clear")
        await pilot.pause()
        assert app.query_one("#calc-expression").content == ""
```

- [ ] **Step 2:** Run `pytest tests/test_standard_tool.py -v` (fails).
- [ ] **Step 3:** Rewrite `hitung/widgets/standard_tool.py`: compose display + keypad, handle `KeyPressed`, maintain `expression` string, on `key-equals` call `evaluate` with contextual percent preprocessing, save `HistoryRecord(category="standard")`, update `app.ans`.
- [ ] **Step 4:** Run `pytest tests/test_standard_tool.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: button-based standard calculator with contextual percent`.

---

### Task 5: Scientific Calculator (button-based)

**Files:**
- Rewrite: `hitung/widgets/scientific_tool.py`
- Test: `tests/test_scientific_tool.py`

**Interfaces:**
- Consumes: `CalculatorDisplay`, `ScientificKeypad` with `SCIENTIFIC_KEYS`.
- Produces: `ScientificTool(Vertical)` with `on_key_pressed`; handles DEG/RAD toggle button `key-angle`; `x²` inserts `^2`, `xʸ` inserts `^`, `1/x` wraps expression, `eˣ` inserts `exp(`, `|x|` inserts `abs(`, `√` inserts `sqrt(`, `⇄` swaps expression with `ans`.

- [ ] **Step 1:** Write failing tests in `tests/test_scientific_tool.py`:

```python
import pytest
from hitung.app import HitungApp

async def test_trig_and_angle_mode(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        for key in ["key-sin","key-3","key-0","key-rparen","key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert app.query_one("#calc-result").content == "0,5"
        await pilot.click("#key-angle")
        await pilot.pause()
        assert app.settings.angle == "rad"

async def test_swap_expression_with_ans(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("scientific")
        await pilot.pause()
        for key in ["key-2","key-plus","key-3","key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        await pilot.click("#key-swap")
        await pilot.pause()
        assert app.query_one("#calc-expression").content == "5"
```

- [ ] **Step 2:** Run `pytest tests/test_scientific_tool.py -v` (fails).
- [ ] **Step 3:** Rewrite `hitung/widgets/scientific_tool.py` per interfaces.
- [ ] **Step 4:** Run `pytest tests/test_scientific_tool.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: button-based scientific calculator with DEG/RAD and ANS swap`.

---

### Task 6: Unit Data & Conversion Engine Expansion

**Files:**
- Modify: `hitung/data/units.py`
- Modify: `hitung/engines/conversion_engine.py`
- Test: `tests/test_conversions.py`

**Interfaces:**
- Produces: `CATEGORIES` with keys `area`, `length`, `temperature`, `volume`, `mass`, `data`, `speed`, `time`. Each category has all units from design §7 and PRD §5.4.
- `convert_value(value, from_unit, to_unit, category, *, mode=None) -> float` supports Rankine (`r`), nautical mile (`nmi`), stone (`st`), imperial gallon (`imgal`), square inch (`in2`), square yard (`yd2`), square mile (`mi2`), ft/s (`fts`), and IEC data units (`KiB`, `MiB`, `GiB`, `TiB`).

- [ ] **Step 1:** Extend failing tests in `tests/test_conversions.py`:

```python
def test_new_units():
    assert convert_value(1, "r", "c", "temperature") == pytest.approx(-272.5944444444)
    assert convert_value(1, "nmi", "m", "length") == pytest.approx(1852.0)
    assert convert_value(1, "st", "kg", "mass") == pytest.approx(6.35029318)
    assert convert_value(1, "imgal", "l", "volume") == pytest.approx(4.54609)
    assert convert_value(1, "in2", "m2", "area") == pytest.approx(0.00064516)
    assert convert_value(1, "fts", "mps", "speed") == pytest.approx(0.3048)
    assert convert_value(1, "KiB", "B", "data", mode="iec") == 1024.0
    assert convert_value(1, "MiB", "KiB", "data", mode="iec") == 1024.0
```

- [ ] **Step 2:** Run `pytest tests/test_conversions.py -v` (fails).
- [ ] **Step 3:** Update `hitung/data/units.py` with new units; update `hitung/engines/conversion_engine.py` for Rankine and IEC data units.
- [ ] **Step 4:** Run `pytest tests/test_conversions.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: expand unit registry with PRD units`.

---

### Task 7: Converter Widgets & Tool

**Files:**
- Create: `hitung/widgets/converter_tabs.py`
- Create: `hitung/widgets/unit_selector.py`
- Create: `hitung/widgets/numeric_keypad.py`
- Rewrite: `hitung/widgets/converter_tool.py`
- Test: `tests/test_converter_tool.py`

**Interfaces:**
- `ConverterTabs(Horizontal)`: `set_categories(list[tuple[str,str]])`, `value` property, emits `CategoryChanged(category_id)`.
- `UnitSelector(Vertical)`: `set_options(list[tuple[str,str]])`, `value` property, emits `UnitChanged(unit_id)`.
- `NumericKeypad(Vertical)`: `KEYS` includes digits, `key-backspace`, `key-clear`, `key-up`, `key-down`, `key-sign`, `key-dot`; emits `NumericKey(value)`.
- `ConverterTool(Vertical)`: composes tabs, FROM/TO selectors, numeric keypad; live conversion; `↑`/`↓` focus FROM/TO; swap button; history record `category="converter:<cat>"`.

- [ ] **Step 1:** Write failing tests in `tests/test_converter_tool.py`:

```python
import pytest
from hitung.app import HitungApp

async def test_temperature_conversion(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.open_tool("converter")
        await pilot.pause()
        # select temperature tab, set from c to f, enter 100, equals
        await pilot.click("#tab-temperature")
        await pilot.pause()
        for key in ["key-1","key-0","key-0","key-equals"]:
            await pilot.click(f"#{key}")
            await pilot.pause()
        assert "212" in app.query_one("#conv-result").content

async def test_focus_navigation(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(120, 40)) as pilot:
        await pilot.pause()
        app.open_tool("converter")
        await pilot.pause()
        await pilot.click("#key-up")
        await pilot.pause()
        assert app.query_one("#conv-from").has_focus
        await pilot.click("#key-down")
        await pilot.pause()
        assert app.query_one("#conv-to").has_focus
```

- [ ] **Step 2:** Run `pytest tests/test_converter_tool.py -v` (fails).
- [ ] **Step 3:** Implement converter widgets and rewrite `hitung/widgets/converter_tool.py` per interfaces.
- [ ] **Step 4:** Run `pytest tests/test_converter_tool.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: button-based unit converter with tabs and numeric keypad`.

---

### Task 8: Percentage & Tip Screens

**Files:**
- Rewrite: `hitung/widgets/percentage_tool.py`
- Create: `hitung/widgets/tip_tool.py`
- Test: `tests/test_percentage_tip.py`

**Interfaces:**
- `PercentageTool(Vertical)`: mode buttons `X% dari Y`, `Perubahan %`, `Diskon`, `Pajak`; numeric inputs; `Hitung` button; output `Static`.
- `TipTool(Vertical)`: bill input, tip percent quick buttons (5,10,15,20,custom), people −/+, output `Tip Amount`, `Total Bill`, `Per Person`, `Tip per Person`; `Calculate` button.
- Reuses `hitung.engines.percentage_engine` functions.

- [ ] **Step 1:** Write failing tests in `tests/test_percentage_tip.py`:

```python
import pytest
from hitung.app import HitungApp

async def test_percentage_discount(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("percentage")
        await pilot.pause()
        # set mode discount, price 100, percent 10, click hitung
        app.query_one("#pct-price").value = "100"
        app.query_one("#pct-percent").value = "10"
        await pilot.click("#pct-run")
        await pilot.pause()
        assert "90" in app.query_one("#pct-out").content

async def test_tip_calculation(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("tip")
        await pilot.pause()
        app.query_one("#tip-bill").value = "150"
        await pilot.click("#tip-15")
        app.query_one("#tip-people").value = "2"
        await pilot.click("#tip-calc")
        await pilot.pause()
        assert "22,5" in app.query_one("#tip-amount").content
        assert "86,25" in app.query_one("#tip-per-person").content
```

- [ ] **Step 2:** Run `pytest tests/test_percentage_tip.py -v` (fails).
- [ ] **Step 3:** Rewrite `hitung/widgets/percentage_tool.py` and create `hitung/widgets/tip_tool.py` per interfaces.
- [ ] **Step 4:** Run `pytest tests/test_percentage_tip.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: percentage and tip calculators`.

---

### Task 9: Dashboard Rewrite

**Files:**
- Rewrite: `hitung/widgets/dashboard_tool.py`
- Test: `tests/test_dashboard.py`

**Interfaces:**
- `DashboardTool(Vertical)`: quick access cards for `scientific`, `converter`, `percentage`, `tip`; recent calculations (5, Clear All); favorite tools list; search box (Ctrl+K).
- Consumes: `hitung.navigation.default_tools`, `hitung.history.recent_records`.

- [ ] **Step 1:** Write failing test `tests/test_dashboard.py`:

```python
import pytest
from hitung.app import HitungApp

async def test_dashboard_quick_access(tmp_path):
    app = HitungApp(data_dir=tmp_path)
    async with app.run_test(size=(100, 30)) as pilot:
        await pilot.pause()
        app.open_tool("dashboard")
        await pilot.pause()
        assert app.query_one("#quick-scientific")
        await pilot.click("#quick-scientific")
        await pilot.pause()
        assert app._active_tool == "scientific"
```

- [ ] **Step 2:** Run `pytest tests/test_dashboard.py -v` (fails).
- [ ] **Step 3:** Rewrite `hitung/widgets/dashboard_tool.py` per interface.
- [ ] **Step 4:** Run `pytest tests/test_dashboard.py -v` (passes).
- [ ] **Step 5:** Commit: `feat: modern dashboard with quick access and favorites`.

---

### Task 10: App Wiring, Screens, Cleanup, Tests

**Files:**
- Modify: `hitung/app.py`
- Modify: `hitung/screens/help_screen.py`
- Modify: `hitung/screens/settings_screen.py`
- Modify: `hitung/screens/search_screen.py`
- Delete: `hitung/widgets/finance_tool.py`, `electrical_tool.py`, `math_tool.py`, `date_tool.py`, `data_tool.py`, `placeholder_tool.py`, `hitung/engines/finance_engine.py`, `electrical_engine.py`, `math_engine.py`, `date_engine.py`, `data_engine.py`
- Rewrite: `tests/test_app.py`
- Delete: `tests/test_advanced_engines.py`, parts of `tests/test_phase6_edge_cases.py` referencing removed engines
- Test: `tests/test_app.py`

**Interfaces:**
- `HitungApp.compose()` yields `Horizontal(id="shell")` containing `Sidebar(id="sidebar")` and `ContentSwitcher(id="tools")` with only the 10 new tools.
- Global bindings: Ctrl+1 standard, Ctrl+2 scientific, Ctrl+3 converter, Ctrl+H dashboard, Ctrl+K search, Ctrl+F favorites, F1 help, F2 history, F3 settings, Ctrl+Q quit.
- Help screen text updated for button-based usage.

- [ ] **Step 1:** Rewrite failing `tests/test_app.py` covering: sidebar navigation, button input, history persistence with category, settings save, help/history modals, responsive layout at 60×18, too-small terminal message.
- [ ] **Step 2:** Run `pytest tests/test_app.py -v` (fails).
- [ ] **Step 3:** Rewrite `hitung/app.py` compose/bindings; update screens; delete removed modules and tests.
- [ ] **Step 4:** Run `pytest -q` (all tests pass).
- [ ] **Step 5:** Run `python -m tools.screenshot` to regenerate `docs/*.svg`.
- [ ] **Step 6:** Update `README.md` and `KONSEP.md` for KALKULATOR PRO v2.0.
- [ ] **Step 7:** Commit: `feat: wire KALKULATOR PRO app, remove old tools, update tests and docs`.

---

## Self-Review

- **Spec coverage:** Theme (Task 1), navigation (2), core widgets (3), standard calc (4), scientific calc (5), unit data (6), converter (7), percentage/tip (8), dashboard (9), app wiring/cleanup/docs (10). Covers design §7 layout, §8 colors, §6 decisions.
- **Step scan:** Each step is one action with a checkable result. Test steps contain exact assertions; code steps contain exact signatures.
- **Type consistency:** `ToolSpec`, `HistoryRecord`, `Settings`, `evaluate` signatures unchanged and reused across tasks.
- **Review Focus:** Each line has a test in the owning task (percent → Task 4; new units → Task 6; focus nav → Task 7; responsive → Task 10; history category → Task 10).
- **Proportion:** Plan is a decomposition of the design, not a transcript; code bodies are left to implementers except where the design pins values (colors, key sets, unit factors).