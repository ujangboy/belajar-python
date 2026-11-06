# Plan: HITUNG → Calculator Pro (All-in-One Terminal Calculator)

## Goal
Transform the existing single-screen HITUNG calculator TUI into the multi-tool "Calculator Pro" defined in the PRD, while preserving all current working features (parser, history, settings, tests). Deliver incrementally by P0 → P1 → P2, keeping the modular architecture and Textual 8.x conventions.

## Context (audit of current repo)
- Package: `hitung/`, entry `main.py`, Textual 8.x, Python 3.11+.
- Existing features: safe expression parser/evaluator (`engine.py`), Indonesian number formatting (`format.py`), JSON/JSONL history (`history.py`, `storage.py`), tolerant `Settings` (`config.py`), modal screens (history/settings/help/confirm), responsive layout, 112 tests.
- No unit converters, dashboard, sidebar, favorites, search, or advanced calculators yet.
- Storage is file-based (config.json + history.jsonl), not SQLite. Keep this; do not introduce SQLite unless a feature explicitly requires relational queries (none do).

## Constraints
- Do not delete or break existing features/tests.
- No total rewrite; extend incrementally.
- Business logic must stay UI-free and testable (domain modules import no Textual).
- No `eval`/`exec` for user input; validate all numeric input.
- Keep runtime dependency to `textual` only; use stdlib for calculations.
- Preserve tolerant config loading (broken config → backup + defaults, never crash).
- All calculations need unit tests; run `pytest -q` before marking done.

## Key decisions
1. **Navigation model:** Replace single-screen app with a dashboard + sidebar. Use Textual `ContentSwitcher` (or screen push) to swap tool panels without restarting. Keep existing calculator as "Standard" tool.
2. **Tool registration:** Create a registry of tools (id, title, category, factory) in `hitung/tools/registry.py`; dashboard, search, and shortcuts all read from it. This avoids hard-coded menus.
3. **Shared history:** Extend `HistoryRecord` with `category` (e.g. `standard`, `converter:temperature`) and optional `input`/`output` text. Keep backward-compatible `from_dict` (missing category → "standard").
4. **Favorites:** Store favorite tool ids in `config.json` (`favorites: list[str]`). No separate DB.
5. **Settings expansion:** Add fields to `Settings`: `theme` (dark/light), `accent`, `number_format`, `default_angle` (already angle), `history_limit` (optional), `favorites`. Clamp/normalize tolerantly.
6. **Conversion engines:** One generic converter engine driven by factor tables in `data/units.py` + `data/conversion_factors.py`. Temperature and digital storage (SI/IEC) get special-case functions.
7. **Scientific additions:** Add `nCr`, `nPr`, cube root, constants already present. Reuse engine parser; add functions to whitelist.
8. **Math/data/electrical/finance/date engines:** Separate pure modules under `core/` (or `hitung/engines/`) following existing module discipline.
9. **Search:** In-memory filter over tool registry + unit names; no external search library.
10. **Theme:** Keep existing dark theme as default; add light theme variant via Textual theme registration; toggle in settings.

## Proposed module layout (evolution of existing)
```
hitung/
  app.py                    # dashboard host, navigation, global bindings
  config.py                 # expanded Settings
  storage.py                # config + history + favorites (same files)
  history.py                # HistoryRecord + category
  engine.py                 # standard/scientific expression engine
  format.py
  theme.py                  # dark + light themes
  navigation.py             # (new) tool registry + routing
  text.py
  hitung.tcss               # expanded responsive styles
  data/
    units.py                # (new) unit definitions
    conversion_factors.py   # (new) factor tables
  engines/                  # (new) pure calculation modules
    conversion_engine.py
    percentage_engine.py
    finance_engine.py
    date_engine.py
    math_engine.py
    electrical_engine.py
    data_engine.py
  screens/
    dashboard.py            # (new) or keep in app.py
    standard.py             # wrap existing calculator
    scientific.py
    converter.py            # generic converter screen
    percentage.py
    finance.py
    date_time.py
    mathematics.py
    electrical.py
    data_calc.py
    history.py (existing)
    settings.py (existing)
    help.py (existing)
    search.py (new modal)   # optional
  widgets/
    sidebar.py              # (new)
    tool_card.py            # (new) dashboard cards
    converter_form.py       # (new)
    result_panel.py         # (new)
    favorites_panel.py      # (new)
  tests/
    test_engine.py (existing)
    test_conversions.py (new)
    test_percentage.py (new)
    test_finance.py (new)
    test_math.py (new)
    test_data.py (new)
    test_electrical.py (new)
    test_date.py (new)
    test_app.py (existing + new flows)
```
Note: adapt to existing `screens/`/`widgets/` naming; avoid duplicate folders.

## Phases

### Phase 1 — Foundation & Navigation (P0)
- Audit & keep existing tests green.
- Add tool registry + categories.
- Build dashboard screen with sidebar, search box, quick access, recent calculations, favorites placeholders.
- Global bindings: Ctrl+Q quit, Ctrl+H dashboard, Ctrl+K search, Ctrl+1 standard, Ctrl+2 scientific, Ctrl+3 converter, Esc back, Enter confirm.
- ContentSwitcher to host tools; back-to-dashboard.
- Favorites persistence in config.
- Keep existing calculator functional inside new host.

Deliverable: app opens to dashboard; can open standard calculator and return.

### Phase 2 — Core Calculators (P0)
- Standard calculator (existing, wrapped).
- Scientific calculator screen reusing engine with DEG/RAD toggle.
- Add missing scientific functions: nCr, nPr, cbrt, maybe log base n.
- Error handling & live preview.
- Copy result.

Deliverable: standard + scientific fully working with tests.

### Phase 3 — Unit Converters (P0 core + P1 rest)
P0: Temperature, Length, Weight, Volume, Digital Storage.
P1: Area, Speed, Time, Pressure, Energy, Power, Angle.
- Generic converter UI: from/to selects, input, swap, all-conversions list.
- Digital storage SI/IEC toggle.
- Time converter with documented month/year assumptions.

Deliverable: all converters from PRD.

### Phase 4 — Everyday & Advanced Tools (P1)
- Percentage (all variants), Discount, Tax (user-set rate), Tip.
- Date & Time (difference, add/subtract days, age, Unix timestamp).
- Finance (simple/compound interest, loan, installment, savings) with formulas.
- Math (GCD, LCM, primes, factorization, mean, median, mode, stddev, permutations, combinations).
- Data/number system (bin/dec/hex, bitwise).
- Electrical (Ohm's law variants) with formulas/units.

Deliverable: all P1 tools.

### Phase 5 — UI/UX Polish (P1/P2)
- Dark/light theme + accent color setting.
- Decimal precision, thousands separator, number format.
- History screen enhancements: category filter, reuse input, delete one/all.
- Favorites panel on dashboard.
- Search overlay (global).
- Responsive layout checks at 60×18 … 140×40.
- Keyboard shortcut consistency.

### Phase 6 — Testing & Optimization (P2)
- Unit tests for every engine.
- Integration tests for navigation and each tool flow via `run_test`.
- Edge cases: division by zero, overflow, domain errors, invalid units.
- Cross-platform smoke (Windows/Linux/macOS) where possible.
- Performance/memory check.

## Data & compatibility
- History schema v2 adds `category` (default "standard") and optional `input`/`output`. Readers tolerate v1.
- Config schema v2 adds new fields with defaults; `from_dict` ignores unknowns.
- Keep `HITUNG_DATA_DIR` override for tests.
- No migration script needed (tolerant readers).

## Validation plan
- `python -m pytest -q` all green (target: existing 112 + new tests).
- Manual smoke: dashboard navigation, each P0 tool, resize, theme toggle, history persistence after restart.
- No `eval`/`exec`; grep for unsafe calls.
- Lint: `ruff check` if configured.

## Risks & mitigations
- Scope creep: strictly follow P0→P1→P2; ship P0 first.
- UI complexity: use native Textual widgets; avoid custom rendering unless needed.
- Floating-point precision in finance: use `Decimal` for money.
- Large history: keep JSONL append; optional limit later.
- Backward compat: tolerant parsers for config/history.

## Open questions
- None blocking; proceed with P0 unless user narrows scope.
