# KONSEP KALKULATOR PRO — Kalkulator TUI

Dokumen ini menjelaskan **apa, kenapa, dan bagaimana** KALKULATOR PRO
dibangun: konsep produk, keputusan desain, arsitektur, model data, sampai
strategi pengujian. Untuk cara pakai sehari-hari lihat [README.md](README.md).

- Versi dokumen: 2.0 (versi aplikasi `2.0.0`)
- Status: v2 selesai — 171 test lulus
- Basis: Python 3.11+ · [Textual](https://textual.textualize.io/) 8.2

---

## 1. Ringkasan

**KALKULATOR PRO** adalah kalkulator berbasis terminal (TUI) dengan
antarmuka tombol. Pengguna memilih alat dari sidebar (kalkulator standar,
ilmiah, konverter unit, persentase, tip), mengklik angka dan operator, dan
melihat hasil besar di display. Keyboard tetap tersedia untuk pengguna yang
lebih suka mengetik.

Berbeda dari v1 yang hanya satu kartu dengan input teks, v2 menambahkan
**navigasi multi-alat**, **keypad tombol**, **konverter 8 kategori**,
**persentase & tip**, **dashboard dengan favorit**, dan **tema terang**.
Semua data tetap lokal, tanpa jaringan.

> Kalimat penjaga arah: *"Kalkulator terminal yang terasa seperti aplikasi
> — bukan repl matematika, bukan spreadsheet."*

---

## 2. Masalah & tujuan

Menghitung cepat di terminal biasanya berarti salah satu dari ini:

1. buka kalkulator grafis (pindah konteks, pakai mouse),
2. ketik ekspresi sekali pakai ke `python -c` / `bc` (hasil hilang),
3. hitung manual di kepala (rawan salah).

KALKULATOR PRO menutup celah itu:

| Tujuan | Ukuran keberhasilan |
| --- | --- |
| Menghitung tanpa pindah konteks | aplikasi start < 1 detik di terminal biasa |
| Hasil bisa dipercaya | semua evaluasi lewat parser sendiri + 171 test |
| Bisa mengulang pekerjaan | riwayat persisten + recall `↑`/`↓` |
| Tanpa risiko `eval` | tidak ada pemanggilan `eval`/`exec` untuk input pengguna |
| Tetap ringan | satu dependency runtime: `textual` |
| Ramah pemula | tombol besar, pesan error Bahasa Indonesia, bantuan `F1` |

---

## 3. Pengguna sasaran

- **Pelajar Python / pengguna terminal** yang ingin melihat contoh aplikasi
  TUI utuh yang rapi, bukan sekadar skrip.
- **Pengguna harian** yang menghitung angka kecil-menengah sambil bekerja
  di terminal (harga, persen, konversi, tip).
- **Pengguna Windows** yang lebih nyaman dengan `run.cmd` satu klik daripada
  mengurus venv.

Asumsi kemampuan: bisa mengklik tombol dan mengetik angka; **tidak**
diasumsikan paham Python.

---

## 4. Prinsip desain

1. **Tombol dulu, keyboard tetap.** Semua aksi punya tombol yang bisa
   diklik; pintasan keyboard adalah jalur cepat, bukan satu-satunya jalan.
2. **Satu layar, satu alat.** Sidebar memilih alat; area kanan menampilkan
   alat aktif. Modal hanya untuk riwayat, pengaturan, bantuan, pencarian,
   dan konfirmasi.
3. **Hasil adalah bintang.** Display hasil besar dan tombol operator besar;
   elemen sekunder memakai warna muted.
4. **Data lokal & transparan.** Dua file JSON/JSONL yang bisa dibaca mata
   manusia; tidak ada database, tidak ada akun.
5. **Error adalah pesan, bukan stack trace.** Setiap kegagalan input
   diterjemahkan jadi satu kalimat Bahasa Indonesia.
6. **Konsisten dengan keluarga project.** Struktur `app/config/engine/
   storage/theme/screens/widgets`, gaya README, `run.cmd`, dan tooling
   mengikuti pola project sebelumnya.

---

## 5. Fitur

### 5.1 Fitur v2 (sudah ada)

| # | Fitur | Ringkasan | Status |
| --- | --- | --- | --- |
| F1 | Parser ekspresi | tokenizer + recursive descent; prioritas operator, kurung, unary, pangkat kanan-asosiatif | ✅ |
| F2 | Operator kalkulator | `+ - * / ^ % !` dan `( )` | ✅ |
| F3 | Fungsi & konstanta | 17 fungsi; `pi`, `e`, `tau`, `ans` | ✅ |
| F4 | Kalkulator standar | Keypad tombol angka + operator harian | ✅ |
| F5 | Kalkulator ilmiah | Trigonometri, log, pangkat, akar, faktorial, DEG/RAD | ✅ |
| F6 | Konverter unit | 8 kategori, FROM/TO, swap, keypad numerik, hasil langsung | ✅ |
| F7 | Persentase | X% dari Y, perubahan %, diskon, pajak | ✅ |
| F8 | Tip | Persen cepat/custom, jumlah orang, empat output | ✅ |
| F9 | Dashboard | Akses cepat, 5 riwayat terakhir, favorit, pencarian alat | ✅ |
| F10 | Favorit | `Ctrl+D` menandai alat; tampil di dashboard; tersimpan di config | ✅ |
| F11 | Riwayat persisten | `history.jsonl`; dashboard + layar riwayat dengan grafik 7 hari | ✅ |
| F12 | Recall ekspresi | `↑`/`↓` memanggil ulang ekspresi unik terbaru | ✅ |
| F13 | Format Indonesia | titik ribuan, koma desimal, notasi ilmiah otomatis | ✅ |
| F14 | Tema & aksen | gelap/terang, aksen blue/mint/amber | ✅ |
| F15 | Salin hasil | `Ctrl+Y` lewat OSC 52 | ✅ |
| F16 | Responsif | min 60 × 18; sidebar disembunyikan < 90 kolom | ✅ |
| F17 | Data lokal | `%APPDATA%\Hitung\` (Windows), XDG (Linux), dll. | ✅ |
| F18 | Test & docs | 171 test pytest; screenshot SVG otomatis; README + KONSEP | ✅ |

### 5.2 Non-goals v2

- Memori tombol `M+ / M- / MR / MC` → cukup `ans`.
- Variabel bernama (`x = 5`, `f(x)`), grafik fungsi, matriks.
- Mode programmer (hex/bin) dan kurs online.
- Multi-baris / skrip ekspresi.
- Cloud sync, akun, atau berbagi riwayat lewat jaringan.
- Notifikasi OS / system tray.

Alasan umum: v2 harus **kecil, selesai, dan enak dipakai**. Setiap fitur di
atas menambah UI dan state yang belum perlu.

---

## 6. Alur pemakaian

### Skenario A — hitung dengan tombol

```text
Ctrl+1 → kalkulator standar
klik 2, 0, 0, ×, 1, 5, %  → display 30 (preview biru)
klik =                     → hasil final mint + masuk riwayat
```

### Skenario B — konversi suhu

```text
Ctrl+3 → konverter
klik tab Temperature → FROM °C, TO °F
ketik 100 di keypad      → panel TO langsung 212
klik ⇄                   → arah dibalik
```

### Skenario C — tip bersama teman

```text
buka Tip → bill 150 → klik 15% → people 2 → Hitung
Tip Amount 22,5 · Total 172,5 · Per Person 86,25 · Tip per Person 11,25
```

### Skenario D — memeriksa pekerjaan lama

```text
F2 → layar riwayat: total · hari ini · 7 hari
     grafik batang per hari + daftar hitungan terbaru
     Hapus semua → modal konfirmasi → riwayat bersih
```

---

## 7. Arsitektur

### 7.1 Lapisan

```text
┌──────────────────────────────────────────────────────────────┐
│  UI (Textual)                                                │
│  app.py · screens/* · widgets/* · hitung.tcss · theme.py    │
│  → tampilan, fokus, binding, routing alat, alur event        │
├──────────────────────────────────────────────────────────────┤
│  Domain murni (tanpa UI, mudah diuji)                        │
│  engine.py            → ekspresi → angka (atau CalcError)    │
│  format.py            → angka     → teks tampilan Indonesia  │
│  history.py           → record    → agregasi 7 hari/recall   │
│  navigation.py        → registry alat + pencarian            │
│  engines/conversion…  → satuan    → hasil konversi           │
│  engines/percentage…  → mode persen/tip → nominal            │
├──────────────────────────────────────────────────────────────┤
│  I/O lokal                                                   │
│  config.py  → Settings + lokasi data per OS                  │
│  storage.py → config.json (atomik) + history.jsonl (append)  │
└──────────────────────────────────────────────────────────────┘
```

**Aturan dependensi (dijaga manual):**

- `engine.py`, `format.py`, `history.py`, `navigation.py`, dan seluruh
  `engines/*` **tidak boleh** mengimpor Textual. Ini yang membuat test
  domain berjalan tanpa terminal.
- `storage.py` hanya bergantung pada `config.py` dan `history.py`.
- Arah sebaliknya (domain → UI) tidak pernah terjadi.

### 7.2 Tanggung jawab modul

| Modul | Tanggung jawab | Tidak boleh |
| --- | --- | --- |
| `engine.py` | tokenize, parse, evaluasi, pesan error matematis | tahu soal Textual, config, atau file |
| `format.py` | angka → string Indonesia; presisi; ribuan; ilmiah | melakukan evaluasi |
| `history.py` | `HistoryRecord`, hitungan per hari, recall, serialisasi | menulis file |
| `navigation.py` | `ToolSpec`, daftar alat, pencarian kata kunci | merender widget |
| `data/units.py` | definisi kategori & satuan konverter | melakukan konversi |
| `engines/*` | konversi satuan, persentase, tip | mengurus UI atau file |
| `config.py` | `Settings`, validasi toleran, lokasi data | menyimpan ke disk |
| `storage.py` | baca/tulis `config.json` & `history.jsonl` | mengurus UI |
| `app.py` | komposisi layar, routing alat, state ans, binding, modal | melakukan aritmetika sendiri |
| `widgets/*` | render alat (display, keypad, sidebar, dashboard, dsb.) | menyimpan state global |
| `screens/*` | modal riwayat/pengaturan/bantuan/pencarian/konfirmasi | mengubah data tanpa lewat app/storage |

### 7.3 Kenapa `engine.py` dipisah?

Karena inti produk ini adalah **kebenaran hasil hitung**. Dengan memisahkan
parser dari UI:

- test domain cepat (tanpa event loop, tanpa terminal);
- bug aritmetika tidak bisa "disembunyikan" oleh layout;
- mesin bisa dipakai ulang (CLI, web, notifikasi) tanpa menyalin kode.

Pemisahan yang sama dipakai untuk `conversion_engine.py` dan
`percentage_engine.py`.

### 7.4 Kenapa `ContentSwitcher`?

Semua alat tetap ter-mount; `ContentSwitcher` hanya mengganti yang terlihat.
Konsekuensinya, id widget harus unik antar-alat. Karena itu kalkulator
ilmiah memakai prefix `sci-`, konverter `conv-`, dan tip `tip-`. Pola ini
lebih murah daripada mount/unmount alat dan menjaga state alat tetap hidup
saat berpindah tab.

---

## 8. Struktur folder

```text
kalkulator TUI/
├─ run.cmd                  # launcher Windows: cari Python, install dep, jalankan
├─ main.py                  # entry point `python main.py`
├─ pyproject.toml           # metadata + console script hitung/kalkulator
├─ requirements.txt         # textual
├─ requirements-dev.txt     # + pytest, pytest-asyncio, textual-dev
├─ pytest.ini               # asyncio_mode=auto, testpaths, pythonpath
├─ README.md                # cara pakai (end-user)
├─ KONSEP.md                # dokumen ini
├─ docs/                    # screenshot SVG (dibuat tools/screenshot.py)
├─ hitung/
│  ├─ app.py                # App Textual, sidebar, routing, binding
│  ├─ navigation.py         # registry alat + pencarian
│  ├─ engine.py             # parser & evaluator
│  ├─ format.py             # format angka
│  ├─ history.py            # record + agregasi
│  ├─ config.py             # settings + path data
│  ├─ storage.py            # config.json & history.jsonl
│  ├─ theme.py              # palet + Theme Textual
│  ├─ text.py               # helper shorten()
│  ├─ hitung.tcss           # seluruh styling
│  ├─ data/units.py         # kategori & satuan konverter
│  ├─ engines/
│  │  ├─ conversion_engine.py
│  │  ├─ percentage_engine.py
│  │  └─ util.py
│  ├─ screens/
│  │  ├─ confirm.py         # modal konfirmasi generik
│  │  ├─ help_screen.py     # bantuan
│  │  ├─ history_screen.py  # riwayat lengkap + hapus
│  │  ├─ search_screen.py   # pencarian alat global
│  │  └─ settings_screen.py # pengaturan
│  └─ widgets/
│     ├─ sidebar.py         # navigasi kiri
│     ├─ display.py         # ekspresi + hasil besar
│     ├─ keypad.py          # keypad standar & ilmiah
│     ├─ numeric_keypad.py  # keypad konverter
│     ├─ converter_tabs.py  # tab kategori
│     ├─ unit_selector.py   # panel FROM/TO
│     ├─ standard_tool.py
│     ├─ scientific_tool.py
│     ├─ converter_tool.py
│     ├─ percentage_tool.py
│     ├─ tip_tool.py
│     ├─ dashboard_tool.py
│     └─ week_chart.py      # grafik batang 7 hari
├─ tests/
│  ├─ test_engine.py
│  ├─ test_format.py
│  ├─ test_config.py
│  ├─ test_history.py
│  ├─ test_storage.py
│  ├─ test_navigation.py
│  ├─ test_theme.py
│  ├─ test_conversions.py
│  ├─ test_core_widgets.py
│  ├─ test_standard_tool.py
│  ├─ test_scientific_tool.py
│  ├─ test_converter_tool.py
│  ├─ test_percentage_tip.py
│  ├─ test_dashboard.py
│  ├─ test_app.py
│  └─ test_phase6_edge_cases.py
└─ tools/
   ├─ screenshot.py         # generate docs/*.svg
   └─ svg_dump.py           # SVG → grid teks (verifikasi layout)
```

---

## 9. Model data

### 9.1 `config.json`

```json
{
  "precision": 6,
  "thousands": true,
  "angle": "deg",
  "sound": true,
  "theme": "dark",
  "accent": "mint",
  "number_format": "id",
  "history_limit": 0,
  "favorites": ["scientific", "converter"],
  "version": 2
}
```

| Field | Tipe | Rentang/nilai | Default | Perilaku kalau aneh |
| --- | --- | --- | --- | --- |
| `precision` | int | 0–10 | 6 | di-clamp; non-angka → default |
| `thousands` | bool | true/false | true | string `"on"/"off"/"ya"` diterima |
| `angle` | str | `"deg"`, `"rad"` | `"deg"` | `derajat/radian/degree…` dinormalkan |
| `sound` | bool | true/false | true | tolerant seperti `thousands` |
| `theme` | str | `"dark"`, `"light"` | `"dark"` | nilai asing → default |
| `accent` | str | `"blue"`, `"mint"`, `"amber"`, `"rose"` | `"blue"` | nilai asing → default |
| `number_format` | str | `"id"`, `"plain"` | `"id"` | nilai asing → default |
| `favorites` | list[str] | id alat | `[]` | item bukan string/duplikat dibuang |
| `history_limit` | int | ≥ 0 (0 = tanpa batas) | 0 | non-angka → default |

Aturan penulisan: `config.json.tmp` → `os.replace` (atomik). Kalau file
rusak, disalin ke `config.json.bak` lalu aplikasi memakai default — tidak
pernah crash karena config.

### 9.2 `history.jsonl`

Satu baris = satu hitungan yang dijalankan (`=`, Hitung, atau konversi
otomatis):

```json
{"at": "2026-11-06T09:00:00+07:00", "expression": "12 + 3 * (4 - 1)", "result": "21", "value": 21.0, "category": "standard"}
```

| Field | Tipe | Catatan |
| --- | --- | --- |
| `at` | ISO datetime | waktu lokal (punya offset) saat disimpan |
| `expression` | str | ekspresi atau label alat (`percentage:discount`, `converter:temperature`, `tip …`) |
| `result` | str | hasil yang sudah diformat (untuk ditampilkan ulang) |
| `value` | float | nilai mentah (untuk analisis/ekspor) |
| `category` | str | `standard`, `scientific`, `converter:<kategori>`, `percentage`, `tip` |

Baris rusak atau field tidak valid **dilewati** saat dibaca; satu baris
korup tidak menghapus riwayat lain. Penulisan memakai append + `flush` +
`fsync` supaya tidak hilang saat terminal ditutup mendadak.

### 9.3 Lokasi data

| OS | Folder |
| --- | --- |
| Windows | `%APPDATA%\Hitung\` |
| macOS | `~/Library/Application Support/Hitung/` |
| Linux | `${XDG_DATA_HOME:-~/.local/share}/hitung/` |
| Override | `$env:HITUNG_DATA_DIR` (dipakai test & pengguna lanjutan) |

---

## 10. Bahasa ekspresi

### 10.1 Grammar (ringkas, EBNF)

```text
expression  = term { ("+" | "-") term } ;
term        = unary { ("*" | "/") unary } ;
unary       = ("+" | "-") unary | power ;
power       = postfix [ "^" unary ] ;            (* kanan-asosiatif *)
postfix     = primary { "%" | "!" } ;
primary     = number | "(" expression ")"
            | name [ "(" expression ")" ] ;
number      = digit { digit } [ ("," | ".") digit { digit } ] ;
name        = letter { letter | digit | "_" } ;   (* dikonversi lowercase *)
```

### 10.2 Semantik

| Aturan | Keputusan | Contoh |
| --- | --- | --- |
| Prioritas | `^` > unary > `%/!` > `* /` > `+ -` | `2+3*4 = 14` |
| Pangkat | kanan-asosiatif | `2^3^2 = 512` |
| Unary minus | lebih lemah dari `^` | `-2^2 = -4` |
| `%` | akhiran "bagi 100" | `200*15% = 30`, `50% = 0,5` |
| `!` | faktorial bilangan bulat 0–170 | `5! = 120`, `(-1)!` → error |
| Desimal | koma **atau** titik | `1,5` = `1.5` |
| Simbol `×`/`÷` | tombol mengirim `*`/`/` | sama dengan v1 |
| Nama | case-insensitive, fungsi butuh kurung | `SQRT(9)`, `pi` |
| `ans` | nilai hasil commit terakhir, default 0 | `ans + 1` |

### 10.3 Daftar fungsi

`sqrt, cbrt, abs, sin, cos, tan, asin, acos, atan, log (basis 10), ln,
log10, exp, floor, ceil, round, ncr, npr` — domain dijaga:
`sqrt(x<0)`, `log/ln(x<=0)`, `asin/acos(|x|>1)`, `tan(90°)` → `CalcError`
dengan pesan Bahasa Indonesia.

### 10.4 Pesan error (contoh)

| Situasi | Pesan |
| --- | --- |
| input kosong | `Ekspresi masih kosong` |
| `2+` | `Ekspresi belum lengkap` |
| `(1+2` | `Kurung tutup ')' kurang` |
| `1/0` | `Pembagian dengan nol tidak terdefinisi` |
| `sqrt(-1)` | `Akar kuadrat butuh nilai >= 0` |
| `foo(1)` | `Nama tidak dikenal: 'foo'` |
| `2@3` | `Karakter tidak dikenal: '@'` |
| `9^999` | `Hasil terlalu besar untuk dihitung` |

Semua error mewarisi `CalcError(ValueError)` sehingga lapisan UI cukup
menangkap satu tipe.

---

## 11. Format angka & presisi

Aturan `format_number(value, precision, thousands, number_format)`:

1. `0` → `"0"` (termasuk `-0`); tak hingga → `"Tak terhingga"`.
2. `|x| ≥ 10^12` → notasi ilmiah (`1,5e+15`).
3. Bulatkan **setengah ke atas** (bukan banker's rounding): `2,5 → 3`.
4. Kalau hasil pembulatan `0` padahal nilai bukan nol → notasi ilmiah.
5. Buang nol di belakang koma; koma sebagai desimal untuk format `id`.
6. Kalau `thousands = true`, kelompokkan ribuan dengan titik.

Presisi disimpan di config dan dipakai saat menampilkan **dan** menyimpan
`result` di riwayat. Nilai mentah tetap disimpan di `value`.

---

## 12. State UI & event

State yang dipegang `HitungApp`:

| State | Arti |
| --- | --- |
| `settings` | `Settings` aktif (dari `config.json`) |
| `records` | cache list `HistoryRecord` (disk tetap sumber kebenaran) |
| `ans` | nilai numerik hasil commit terakhir |
| `last_expression`, `last_result` | untuk baris "terakhir:" dan salin |
| `_recall`, `_recall_index` | daftar ekspresi unik + posisi panah |
| `_active_tool` | id alat yang sedang tampil |
| `_pending_input` | penanda nilai input yang di-set program (bukan ketikan) |

Event penting:

| Event | Reaksi |
| --- | --- |
| `Button.Pressed` | diteruskan ke alat aktif (keypad, mode, hitung) |
| `Input.Changed` | di dashboard: filter daftar alat |
| `Input.Submitted` | hitung (standar/ilmiah) |
| `Select.Changed` | ganti satuan/opsi di konverter & pengaturan |
| `Ctrl+1/2/3/H/K/F/D` | routing alat, pencarian, favorit |
| `Esc` | bersihkan entri atau kembali ke dashboard |
| `F2` / `F3` / `F1` | riwayat / pengaturan / bantuan |
| `Resize` | tampilkan pesan terminal kecil atau sembunyikan sidebar |

Catatan implementasi: `ContentSwitcher` mempertahankan semua alat tetap
ter-mount. Karena itu id widget diberi prefix per alat, dan pesan kustom
membawa id pengirim bila `Message.control` tidak tersedia.

---

## 13. Peta tombol & alasannya

| Tombol | Aksi | Alasan |
| --- | --- | --- |
| *klik* | semua aksi utama | UI v2 berbasis tombol |
| `Ctrl+1/2/3` | standar/ilmiah/konverter | tiga alat paling sering |
| `Ctrl+H` | dashboard | "home" |
| `Ctrl+K` | cari alat | konvensi command palette |
| `Ctrl+F` / `Ctrl+D` | lihat / tandai favorit | F = favorite, D = designate |
| `Ctrl+Y` | salin hasil | tidak bentrok dengan mengetik |
| `↑` `↓` | recall ekspresi / pindah FROM-TO | konvensi shell & form |
| `Esc` | bersihkan / kembali | konvensi modal/editor |
| `F1`–`F3` | bantuan/riwayat/atur | F-key bebas dari konflik teks |
| `Ctrl+Q` | keluar | konvensi Textual |

Huruf tunggal tidak dipakai karena input teks masih menerima nama fungsi
seperti `sin`, `cos`, `tan`, dan `sqrt`.

---

## 14. Responsivitas & batas ukuran

| Lebar terminal | Yang tampil |
| --- | --- |
| < 60 atau tinggi < 18 | hanya pesan "Terminal terlalu kecil — minimal 60 × 18" |
| 60–89 | area alat penuh, sidebar disembunyikan |
| ≥ 90 | sidebar 14 kolom + area alat |
| Dashboard | kartu akses cepat 4 kolom, daftar alat, panel riwayat/favorit |

Alasan sidebar disembunyikan di 60–89: keypad dan display butuh lebar
minimum agar tombol tidak terpotong. Navigasi tetap bisa lewat `Ctrl+H`,
`Ctrl+1/2/3`, dashboard, atau pencarian `Ctrl+K`.

---

## 15. Strategi testing

### 15.1 Piramida

```text
        ┌──────────────────────────────┐
        │  test_app.py + tool tests    │  integrasi Textual run_test
        ├──────────────────────────────┤
        │ domain murni                 │  engine · format · history ·
        │                              │  conversion · percentage · nav
        ├──────────────────────────────┤
        │ I/O                          │  config · storage (tmp_path)
        └──────────────────────────────┘
```

### 15.2 Cakupan

| File | Fokus |
| --- | --- |
| `test_engine.py` | ekspresi parametris, error, fungsi/konstanta/`ans`/mode sudut |
| `test_format.py` | kombinasi nilai/opsi, clamp presisi, ilmiah, non-finite |
| `test_config.py` | default, clamp, toleransi tipe, favorit, round-trip, env override |
| `test_history.py` | hitungan hari ini/7 hari, urutan terbaru, recall unik, serialisasi |
| `test_storage.py` | round-trip, backup config rusak, JSONL toleran, hapus riwayat |
| `test_navigation.py` | urutan 10 alat, metadata, pencarian kata kunci |
| `test_theme.py` | palet gelap/terang, aksen, fallback nilai asing |
| `test_conversions.py` | akurasi unit baru: Rankine, mil laut, stone, galon imperial, mil persegi, ft/s, data IEC |
| `test_core_widgets.py` | sidebar, display, keypad standar/ilmiah |
| `test_standard_tool.py` | alur tombol standar, preview, commit, error |
| `test_scientific_tool.py` | fungsi ilmiah, DEG/RAD, keypad |
| `test_converter_tool.py` | konversi suhu, swap, tab, keypad |
| `test_percentage_tip.py` | diskon, mode persen, tip, per orang |
| `test_dashboard.py` | akses cepat, riwayat, favorit, pencarian |
| `test_app.py` | routing alat, sidebar, pintasan global, modal, resize, persistensi |
| `test_phase6_edge_cases.py` | error engine & konversi, format ekstrem |

Total saat dokumen ini ditulis: **171 test, semua lulus** (`pytest -q`).

### 15.3 Prinsip test

- Domain diuji tanpa UI; UI diuji lewat `app.run_test()` + `pilot`.
- Data selalu di `tmp_path` lewat `HitungApp(data_dir=...)` — tidak pernah
  menyentuh data pengguna asli.
- Jam/tanggal tidak di-mock kecuali perlu; fungsi agregasi menerima
  parameter `today` supaya deterministik.
- Screenshot (`tools/screenshot.py`) memakai data seed di folder sementara
  dan `export_screenshot()`, jadi tidak butuh terminal sungguhan.

---

## 16. Keputusan teknis & alasannya

| Keputusan | Alternatif | Alasan dipilih |
| --- | --- | --- |
| Parser sendiri | `eval()`, `ast.literal_eval`, `numexpr` | `eval` berbahaya; parser sendiri teruji dan jadi bahan belajar |
| Recursive descent | shunting-yard | lebih mudah dibaca dan ditambah fungsi |
| Textual | Rich langsung, prompt_toolkit, curses | widget siap pakai, `run_test` untuk integrasi, styling TCSS |
| UI tombol + ContentSwitcher | satu input teks | target v2 adalah tombol; alat tetap hidup saat berpindah |
| Prefix id per alat | mount/unmount alat | id unik tanpa kehilangan state, lebih murah |
| JSONL untuk riwayat | SQLite, pickle | append-only, aman dari korupsi sebagian, mudah dibaca |
| Atomik write config | tulis langsung | config tidak setengah tertulis kalau proses mati |
| Pembulatan half-up | banker's rounding | sesuai harapan orang awam (`2,5 → 3`) |
| `ans` bukan memori M+/MR | memori klasik | lebih sederhana dan lebih kuat untuk merangkai (`ans*2`) |
| Satu dependency | sebanyak mungkin | instalasi via `run.cmd` cepat dan tahan banting |
| Error Bahasa Indonesia | Inggris | pengguna sasaran pemula Indonesia |

---

## 17. Risiko & mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Presisi `float` | hasil desimal panjang terlihat "aneh" | format presisi + dokumen batasan; nilai mentah disimpan |
| Clipboard OSC 52 tidak didukung | `Ctrl+Y` tidak menyalin | hasil tetap di layar & riwayat; pesan di troubleshooting |
| Dua instance bersamaan | baris JSONL bercampur | append per baris tetap valid; didokumentasikan sebagai batasan |
| Riwayat tumbuh besar | file besar | `F2 → Hapus semua` / Clear All; roadmap: rotasi |
| Terminal terlalu kecil | layout rusak | pesan khusus + sidebar adaptif + keypad responsif |
| Id widget bentrok antar-alat | query salah widget | prefix `sci-`/`conv-`/`tip-` + test integrasi |
| Perubahan Textual (versi mayor) | API bergeser | pin `textual>=8.2,<9.0`; test UI menandai regresi |

---

## 18. Roadmap

**v2.1 (kecil, cepat):**

- Memori `M+ / M- / MR / MC` dengan indikator di display.
- Batas/rotasi riwayat (mis. 5.000 baris) + ekspor CSV.
- Hapus satu baris riwayat, bukan hanya semua.

**v2.2:**

- Variabel bernama (`x = 5`, `ans` otomatis).
- Fungsi dua argumen (`log(x, base)`, `min`, `max`, `gcd`).
- Riwayat dengan pencarian/filter.

**v3 (kalau masih kecil dan jelas):**

- Grafik fungsi sederhana di terminal (ASCII).
- Tema kustom dari file.
- Kurs mata uang manual (tanpa jaringan).

Semua kandidat harus lolos filter: **tidak menambah mode layar baru
sebelum v2 stabil**.

---

## 19. Definition of Done v2

- [x] `python main.py`, `python -m hitung`, `.\run.cmd` jalan di Windows.
- [x] Semua fitur F1–F18 ada dan bisa dipakai dengan tombol.
- [x] 171 test lulus; tidak ada `eval`/`exec` untuk input pengguna.
- [x] Riwayat & favorit bertahan setelah aplikasi ditutup dan dibuka lagi.
- [x] Config rusak tidak membuat aplikasi crash.
- [x] Terminal 60×18 sampai 140×40 tidak merusak layout.
- [x] Pesan error Bahasa Indonesia untuk semua kegagalan input.
- [x] README + KONSEP + screenshot SVG terbarui.
- [x] Tidak ada dependency runtime selain `textual`.

---

## 20. Referensi

- Textual documentation — <https://textual.textualize.io/>
- Repo project: <https://github.com/ujangboy/belajar-python>
- Sibling project sebagai acuan struktur: `03_Mini_Projects/pomodoro_tui`
  (FOKUS — pomodoro TUI)
- Panduan cara pakai: [README.md](README.md)
