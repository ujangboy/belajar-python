# KONSEP HITUNG — Kalkulator TUI

Dokumen ini menjelaskan **apa, kenapa, dan bagaimana** HITUNG dibangun:
konsep produk, keputusan desain, arsitektur, model data, sampai rencana
pengujian. Untuk cara pakai sehari-hari lihat [README.md](README.md).

- Versi dokumen: 1.0 (versi aplikasi `1.0.0`)
- Status: v1 selesai — 112 test lulus
- Basis: Python 3.11+ · [Textual](https://textual.textualize.io/) 8.2

---

## 1. Ringkasan

**HITUNG** adalah kalkulator berbasis terminal (TUI). Pengguna mengetik
ekspresi seperti `12 + 3 * (4 - 1)` atau `sqrt(144) + 2^3`, melihat hasil
sementara secara langsung, lalu menekan `Enter` untuk menjadikannya hasil
final sekaligus menyimpannya ke riwayat lokal.

Bentuknya sengaja kecil dan tenang: **satu kartu hitung** dengan hasil besar,
**satu panel riwayat** di sampingnya, dan modal tipis untuk riwayat,
pengaturan, bantuan, dan konfirmasi. Semua data lokal, tanpa jaringan.

> Kalimat penjaga arah: *"Kalkulator yang enak dipakai sambil mengetik di
> terminal — bukan CAS, bukan spreadsheet."*

---

## 2. Masalah & tujuan

Menghitung cepat di terminal biasanya berarti salah satu dari ini:

1. buka kalkulator grafis (pindah konteks, pakai mouse),
2. ketik ekspresi sekali pakai ke `python -c` / `bc` (hasil hilang),
3. hitung manual di kepala (rawan salah).

HITUNG menutup celah itu:

| Tujuan | Ukuran keberhasilan |
| --- | --- |
| Menghitung tanpa pindah konteks | aplikasi start < 1 detik di terminal biasa |
| Hasil bisa dipercaya | semua evaluasi lewat parser sendiri + 112 test |
| Bisa mengulang pekerjaan | riwayat persisten + recall `↑`/`↓` |
| Tanpa risiko `eval` | tidak ada pemanggilan `eval`/`exec` untuk input pengguna |
| Tetap ringan | satu dependency runtime: `textual` |
| Ramah pemula | pesan error Bahasa Indonesia, bantuan `F1` lengkap |

---

## 3. Pengguna sasaran

- **Pelajar Python / pengguna terminal** yang ingin melihat contoh aplikasi
  TUI utuh yang rapi, bukan sekadar skrip.
- **Pengguna harian** yang menghitung angka kecil-menengah sambil bekerja
  di terminal (harga, persen, konversi sederhana, cek rumus).
- **Pengguna Windows** yang lebih nyaman dengan `run.cmd` satu klik daripada
  mengurus venv — sama seperti alur project FOKUS sebelumnya.

Asumsi kemampuan: bisa mengetik ekspresi matematika sederhana; **tidak**
diasumsikan paham Python.

---

## 4. Prinsip desain

1. **Preview dulu, simpan belakangan.** Hasil sementara (biru) tidak
   mengotori riwayat; hanya `Enter` yang menyimpan (mint) dan menambah
   hitungan hari itu.
2. **Keyboard-first, tanpa mouse.** Satu input teks; semua aksi punya tombol
   dan muncul di footer/bantuan.
3. **Satu layar, satu fokus.** Tidak ada tab, menu bertingkat, atau panel
   yang berebut perhatian. Modal hanya untuk hal yang memang sekunder.
4. **Data lokal & transparan.** Dua file JSON/JSONL yang bisa dibaca mata
   manusia; tidak ada database, tidak ada akun.
5. **Error adalah pesan, bukan stack trace.** Setiap kegagalan input
   diterjemahkan jadi satu kalimat Bahasa Indonesia yang menjelaskan apa
   yang salah dan apa yang bisa dilakukan.
6. **Konsisten dengan keluarga project.** Struktur `app/config/engine/
   storage/theme/screens/widgets`, gaya README, `run.cmd`, dan tooling
   mengikuti pola FOKUS (pomodoro TUI) — satu cara untuk belajar banyak hal.

---

## 5. Fitur

### 5.1 Fitur v1 (sudah ada)

| # | Fitur | Ringkasan | Status |
| --- | --- | --- | --- |
| F1 | Parser ekspresi | tokenizer + recursive descent; prioritas operator, kurung, unary, pangkat kanan-asosiatif | ✅ |
| F2 | Operator kalkulator | `+ - * / ^ % !` dan `( )` | ✅ |
| F3 | Fungsi & konstanta | 14 fungsi satu argumen; `pi`, `e`, `tau`, `ans` | ✅ |
| F4 | Preview live | hasil sementara saat mengetik; warna beda dari hasil final | ✅ |
| F5 | Riwayat persisten | `history.jsonl`; panel 5 terakhir + layar riwayat lengkap | ✅ |
| F6 | Recall ekspresi | `↑`/`↓` memanggil ulang ekspresi unik terbaru | ✅ |
| F7 | Ringkasan & grafik | total, hari ini, 7 hari; grafik batang 7 hari | ✅ |
| F8 | Format Indonesia | titik ribuan, koma desimal, notasi ilmiah otomatis | ✅ |
| F9 | Presisi & mode sudut | 0–10 desimal; derajat/radian; bel on/off | ✅ |
| F10 | Salin hasil | `Ctrl+Y` lewat OSC 52 | ✅ |
| F11 | Mode ringkas | sembunyikan topbar/panel/footer (`F4`) | ✅ |
| F12 | Responsif | min 60 × 18, panel disembunyikan < 86 kolom | ✅ |
| F13 | Data lokal | `%APPDATA%\Hitung\` (Windows), XDG (Linux), dll. | ✅ |
| F14 | Test & docs | 112 test pytest; screenshot SVG otomatis; README + KONSEP | ✅ |

### 5.2 Non-goals v1 (sengaja ditunda)

- Memori tombol `M+ / M- / MR / MC` → cukup `ans`.
- Variabel bernama (`x = 5`, `f(x)`), karena membuka pintu ke bahasa
  pemrograman mini (perlu desain resolver dan penyimpanan tambahan).
- Grafik fungsi, konversi satuan, mode programmer (hex/bin), matriks.
- Multi-baris / skrip ekspresi.
- Cloud sync, akun, atau berbagi riwayat lewat jaringan.
- Notifikasi OS / system tray.

Alasan umum: v1 harus **kecil, selesai, dan enak dipakai**. Setiap fitur di
atas menambah UI dan state yang belum perlu pada kalkulator satu kartu.

---

## 6. Alur pemakaian

### Skenario A — hitung sekali pakai

```text
ketik: 200 * 15%
preview: 30            (biru, belum tersimpan)
Enter:  hasil 30 final (mint) + masuk riwayat hari ini
```

### Skenario B — merangkai hasil

```text
12 + 3          → Enter → 15
ans * 2         → preview 30 → Enter → 30
↑               → input kembali ke "ans * 2"
Esc             → input bersih, hasil terakhir tetap tampil
```

### Skenario C — memeriksa pekerjaan lama

```text
F2 → layar riwayat: total 7 hitungan · hari ini 3 · 7 hari 7
     grafik batang per hari + daftar hitungan terbaru
     Hapus semua → modal konfirmasi → riwayat bersih
```

### Alur status utama

```text
                 input teks berubah
   ┌──────────┐  ──────────────────▶  ┌──────────────┐
   │  IDLE    │                       │  PREVIEW     │
   │ (hasil   │  ◀──────────────────  │ (hasil biru) │
   │  terakhir│      tidak valid      └──────┬───────┘
   └────┬─────┘                              │ Enter & valid
        │ Esc                                ▼
        └──────────── input kosong ───  ┌──────────────┐
                                        │  COMMITTED   │
                                        │ hasil mint + │
                                        │ riwayat +ans │
                                        └──────────────┘
```

---

## 7. Arsitektur

### 7.1 Lapisan

```text
┌──────────────────────────────────────────────────────────────┐
│  UI (Textual)                                                │
│  app.py · screens/* · widgets/* · hitung.tcss · theme.py    │
│  → hanya mengurus tampilan, fokus, binding, dan alur event   │
├──────────────────────────────────────────────────────────────┤
│  Domain murni (tanpa UI, mudah diuji)                        │
│  engine.py  → ekspresi → angka (atau CalcError)              │
│  format.py  → angka     → teks tampilan Indonesia            │
│  history.py → record    → agregasi hari ini / 7 hari / recall│
├──────────────────────────────────────────────────────────────┤
│  I/O lokal                                                   │
│  config.py  → Settings + lokasi data per OS                  │
│  storage.py → config.json (atomik) + history.jsonl (append)  │
└──────────────────────────────────────────────────────────────┘
```

**Aturan dependensi (dijaga manual):**

- `engine.py`, `format.py`, `history.py` **tidak boleh** mengimpor Textual.
  Ini yang membuat 60+ test domain bisa berjalan tanpa terminal.
- `storage.py` hanya bergantung pada `config.py` dan `history.py`.
- Arah sebaliknya (domain → UI) tidak pernah terjadi.

### 7.2 Tanggung jawab modul

| Modul | Tanggung jawab | Tidak boleh |
| --- | --- | --- |
| `engine.py` | tokenize, parse, evaluasi, semua pesan error matematis | tahu soal Textual, config, atau file |
| `format.py` | angka → string Indonesia; presisi; ribuan; ilmiah | melakukan evaluasi |
| `history.py` | `HistoryRecord`, hitungan per hari, recall, serialisasi record | menulis file |
| `config.py` | `Settings`, validasi toleran, lokasi data | menyimpan ke disk |
| `storage.py` | baca/tulis `config.json` & `history.jsonl` | mengurus UI |
| `app.py` | komposisi layar, state ans/last/preview, binding, modal | melakukan aritmetika sendiri |
| `widgets/*` | render bagian layar (kartu, panel, grafik) | menyimpan state aplikasi |
| `screens/*` | modal riwayat/pengaturan/bantuan/konfirmasi | mengubah data tanpa lewat app/storage |

### 7.3 Kenapa `engine.py` dipisah?

Karena inti produk ini adalah **kebenaran hasil hitung**. Dengan memisahkan
parser dari UI:

- test domain cepat (tanpa event loop, tanpa terminal);
- bug aritmetika tidak bisa "disembunyikan" oleh layout;
- mesin bisa dipakai ulang (CLI, web, notifikasi) tanpa menyalin kode.

Pemisahan yang sama dipakai FOKUS untuk `timer.py`.

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
│  ├─ __init__.py           # __version__
│  ├─ __main__.py           # `python -m hitung`
│  ├─ app.py                # App Textual
│  ├─ engine.py             # parser & evaluator
│  ├─ format.py             # format angka
│  ├─ history.py            # record + agregasi
│  ├─ config.py             # settings + path data
│  ├─ storage.py            # config.json & history.jsonl
│  ├─ theme.py              # palet + Theme Textual
│  ├─ text.py               # helper shorten()
│  ├─ hitung.tcss           # seluruh styling
│  ├─ screens/
│  │  ├─ confirm.py         # modal konfirmasi generik
│  │  ├─ help_screen.py     # bantuan
│  │  ├─ history_screen.py  # riwayat lengkap + hapus
│  │  └─ settings_screen.py # pengaturan
│  └─ widgets/
│     ├─ topbar.py          # brand, subjudul, jam
│     ├─ calc_card.py       # hasil besar, input, status
│     ├─ history_panel.py   # 5 riwayat terakhir
│     └─ week_chart.py      # grafik batang 7 hari
├─ tests/
│  ├─ test_engine.py        # ~50 test (parametris)
│  ├─ test_format.py
│  ├─ test_config.py
│  ├─ test_history.py
│  ├─ test_storage.py
│  └─ test_app.py           # 20 test integrasi Textual (run_test)
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
  "version": 1
}
```

| Field | Tipe | Rentang/nilai | Default | Perilaku kalau aneh |
| --- | --- | --- | --- | --- |
| `precision` | int | 0–10 | 6 | di-clamp; non-angka → default |
| `thousands` | bool | true/false | true | string `"on"/"off"/"ya"` diterima |
| `angle` | str | `"deg"`, `"rad"` | `"deg"` | `derajat/radian/degree…` dinormalkan |
| `sound` | bool | true/false | true | tolerant seperti `thousands` |
| `version` | int | 1 | 1 | selalu ditulis 1 (skema v1) |

Aturan penulisan: `config.json.tmp` → `os.replace` (atomik). Kalau file
rusak, disalin ke `config.json.bak` lalu aplikasi memakai default — tidak
pernah crash karena config.

### 9.2 `history.jsonl`

Satu baris = satu hitungan yang sudah di-`Enter`:

```json
{"at": "2026-10-25T09:00:00+07:00", "expression": "12 + 3 * (4 - 1)", "result": "21", "value": 21.0}
```

| Field | Tipe | Catatan |
| --- | --- | --- |
| `at` | ISO datetime | waktu lokal (punya offset) saat disimpan |
| `expression` | str | apa yang diketik pengguna, apa adanya |
| `result` | str | hasil yang sudah diformat (untuk ditampilkan ulang) |
| `value` | float | nilai mentah (untuk analisis/ekspor) |

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
| Simbol `×`/`÷` | tidak didukung, gunakan `*`/`/` | — |
| Nama | case-insensitive, fungsi butuh kurung | `SQRT(9)`, `pi` |
| `ans` | nilai hasil commit terakhir, default 0 | `ans + 1` |

### 10.3 Daftar fungsi

`squareroot, abs, sin, cos, tan, asin, acos, atan, log (basis 10), ln,
exp, floor, ceil, round` — semuanya **satu argumen**. Domain dijaga:
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

Aturan `format_number(value, precision, thousands)`:

1. `0` → `"0"` (termasuk `-0`); tak hingga → `"Tak terhingga"`.
2. `|x| ≥ 10^12` → notasi ilmiah (`1,5e+15`).
3. Bulatkan **setengah ke atas** (bukan banker's rounding): `2,5 → 3`.
4. Kalau hasil pembulatan `0` padahal nilai bukan nol → notasi ilmiah
   (mis. `1e-9` → `1e-09`), supaya angka kecil tidak terlihat seperti nol.
5. Buang nol di belakang koma; tampilkan koma sebagai desimal.
6. Kalau `thousands = true`, kelompokkan ribuan dengan titik.

Presisi disimpan di config dan dipakai saat menampilkan **dan** menyimpan
`result` di riwayat (riwayat konsisten dengan yang dilihat pengguna).
Nilai mentah tetap disimpan di `value`.

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
| `_pending_input` | penanda nilai input yang di-set program (bukan ketikan) |
| `_compact` | mode ringkas |

Event penting:

| Event | Reaksi |
| --- | --- |
| `Input.Changed` | kalau bukan nilai program: reset posisi recall, hitung preview |
| `Input.Submitted` | `action_calculate()` |
| `Esc` / `↑` / `↓` / `Ctrl+Y` / `F1`–`F4` / `Ctrl+Q` | binding app (dicek modal dulu) |
| `F2` | buka `HistoryScreen`; hasil callback `True` → reload daftar |
| `F3` | buka `SettingsScreen`; hasil `Settings` → simpan + refresh preview |
| `Resize` | `_update_size()`: pesan terminal kecil / panel samping / mode ringkas |

Catatan implementasi: pesan `Input.Changed` **diproses setelah** kode yang
menyetel `.value` selesai, jadi flag boolean sederhana tidak cukup.
Solusinya `_pending_input` dibandingkan dengan `event.value`, sehingga
perubahan programmatic (setelah commit / recall) tidak dianggap ketikan.

---

## 13. Peta tombol & alasannya

| Tombol | Aksi | Alasan |
| --- | --- | --- |
| *huruf/angka/operator* | menulis ekspresi | fungsi inti aplikasi |
| `Enter` | hitung & simpan | konvensi kalkulator/REPL |
| `Esc` | bersihkan input | konvensi modal/editor |
| `↑` `↓` | recall ekspresi | konvensi shell history |
| `Ctrl+Y` | salin hasil | tidak bentrok dengan mengetik |
| `F1`–`F4` | bantuan/riwayat/atur/ringkas | F-key bebas dari konflik teks |
| `Ctrl+Q` | keluar | konvensi Textual |

**Kenapa bukan huruf tunggal seperti FOKUS?** Karena HITUNG punya input
teks: tombol `s`, `c`, `t`, `q` akan bentrok saat pengguna mengetik `sin`,
`cos`, `tan`, atau `sqrt`. FOKUS boleh memakai huruf tunggal karena tidak
punya input teks. Ini perbedaan desain yang disengaja.

---

## 14. Responsivitas & batas ukuran

| Lebar terminal | Yang tampil |
| --- | --- |
| < 60 atau tinggi < 18 | hanya pesan "Terminal terlalu kecil — minimal 60 × 18" |
| 60–85 | kartu penuh, panel riwayat disembunyikan |
| ≥ 86 | kartu + panel riwayat (lebar 34) |
| `F4` (mode ringkas) | tanpa topbar/panel/footer, hanya kartu + hint |

Alasan panel disembunyikan di 60–85: kartu butuh ruang untuk hasil besar,
input, dan status; memaksa panel di lebar itu membuat semuanya sempit.
Riwayat tetap bisa dibuka penuh lewat `F2`.

---

## 15. Strategi testing

### 15.1 Piramida

```text
        ┌─────────────────────────┐
        │  test_app.py (20 test)  │  integrasi Textual run_test 100×30
        ├─────────────────────────┤
        │ domain murni (≈70 test) │  engine · format · history
        ├─────────────────────────┤
        │ I/O (≈15 test)          │  config · storage (tmp_path)
        └─────────────────────────┘
```

### 15.2 Cakupan

| File | Fokus |
| --- | --- |
| `test_engine.py` | 22 ekspresi parametris + 20 kasus error + fungsi/konstanta/`ans`/mode sudut |
| `test_format.py` | 15 kombinasi nilai/opsi + clamp presisi + ilmiah + non-finite |
| `test_config.py` | default, clamp, toleransi tipe, round-trip, env override |
| `test_history.py` | hitungan hari ini/7 hari, urutan terbaru, recall unik, serialisasi tolerant |
| `test_storage.py` | round-trip, backup config rusak, JSONL toleran, hapus riwayat |
| `test_app.py` | preview live, commit, error, Esc, recall, salin, `ans`, modal, hapus, pengaturan, ringkas, resize, persistensi |

Total saat dokumen ini ditulis: **112 test, semua lulus** (`pytest -q`).

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
| Parser sendiri | `eval()`, `ast.literal_eval`, `numexpr` | `eval` berbahaya; `literal_eval` tidak mendukung operator/fungsi; parser sendiri ~250 baris, teruji, dan jadi bahan belajar |
| Recursive descent | shunting-yard | lebih mudah dibaca dan ditambah fungsi |
| Textual | Rich langsung, prompt_toolkit, curses | widget siap pakai, `run_test` untuk integrasi, styling TCSS |
| JSONL untuk riwayat | SQLite, pickle | append-only, aman dari korupsi sebagian, mudah dibaca/diedit manusia |
| Atomik write config | tulis langsung | config tidak setengah tertulis kalau proses mati |
| Pembulatan half-up | banker's rounding | sesuai harapan orang awam (`2,5 → 3`) |
| `ans` bukan memori M+/MR | memori klasik | lebih sederhana dan lebih kuat untuk merangkai (`ans*2`) |
| Aksi `Ctrl`/F-key | huruf tunggal | input teks memakai huruf (lihat §13) |
| Satu dependency | sebanyak mungkin | instalasi via `run.cmd` cepat dan tahan banting |
| Error Bahasa Indonesia | Inggris | pengguna sasaran pemula Indonesia |

---

## 17. Risiko & mitigasi

| Risiko | Dampak | Mitigasi |
| --- | --- | --- |
| Presisi `float` | hasil desimal panjang terlihat "aneh" | format presisi + dokumen batasan; nilai mentah disimpan |
| Clipboard OSC 52 tidak didukung | `Ctrl+Y` tidak menyalin | hasil tetap di layar & riwayat; pesan di troubleshooting |
| Dua instance bersamaan | baris JSONL bercampur | append per baris tetap valid; didokumentasikan sebagai batasan |
| Riwayat tumbuh besar | file besar | `F2 → Hapus semua`; roadmap: batasi/rotasi |
| Terminal terlalu kecil | layout rusak | pesan khusus + panel adaptif |
| Perubahan Textual (versi mayor) | API bergeser | pin `textual>=8.2,<9.0`; 20 test UI menandai regresi |

---

## 18. Roadmap

**v1.1 (kecil, cepat):**

- Memori `M+ / M- / MR / MC` dengan indikator di kartu.
- Batas/rotasi riwayat (mis. 5.000 baris) + ekspor CSV.
- `Ctrl+R` untuk menghapus satu baris riwayat, bukan hanya semua.

**v1.2 (kalkulator ilmiah):**

- Variabel bernama (`x = 5`, `ans` otomatis).
- Fungsi dua argumen (`log(x, base)`, `min`, `max`, `gcd`).
- Riwayat dengan pencarian/filter.

**v2 (kalau masih kecil dan jelas):**

- Grafik fungsi sederhana di terminal (ASCII).
- Konversi satuan.
- Tema terang + pilihan palet.

Semua kandidat harus lolos filter: **tidak menambah mode layar baru
sebelum v1 stabil**.

---

## 19. Definition of Done v1

- [x] `python main.py`, `python -m hitung`, `.\run.cmd` jalan di Windows.
- [x] Semua fitur F1–F14 ada dan bisa dipakai tanpa mouse.
- [x] 112 test lulus; tidak ada `eval`/`exec` untuk input pengguna.
- [x] Riwayat bertahan setelah aplikasi ditutup dan dibuka lagi.
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
