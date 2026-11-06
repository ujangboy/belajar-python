# KALKULATOR PRO v2.0 — desain

- Tanggal: 2026-11-06
- Status: menunggu persetujuan
- Basis: repo `kalkulator TUI`, Python 3.11+, Textual 8.x, 155 test lulus

## 1. Intent

Rebuild HITUNG menjadi **KALKULATOR PRO** — kalkulator multifungsi berbasis tombol di terminal, seperti aplikasi kalkulator smartphone modern. Pengguna menghitung lewat tombol angka dan fungsi, memilih satuan lewat tab, dan menelusuri alat dari sidebar.

## 2. Goals

- Kalkulator ilmiah berbasis tombol (bukan input ekspresi teks).
- 9 kategori konverter unit: Area, Length, Temperature, Volume, Mass, Data, Speed, Time, Tip.
- Dashboard dengan quick access, riwayat terbaru, dan favorit.
- Navigasi tanpa restart aplikasi.
- Tema modern: dark navy + slate + aksen biru/hijau/oranye.
- Keyboard + mouse.
- Riwayat, favorit, dan pengaturan tersimpan lokal.

## 3. Non-goals

- Tidak ada keuangan, kelistrikan, matematika, tanggal, atau data biner/hex lama.
- Tidak ada grafik fungsi, cloud, akun, atau notifikasi OS.
- Tidak ada migrasi storage ke SQLite (JSONL dipertahankan).

## 4. Constraints

- Engine ekspresi aman (tanpa `eval`) tetap dipakai; UI tidak menempatkan rumus.
- Satu dependency runtime: `textual`.
- Semua data lokal, offline.
- Layout responsif 60×18 sampai lebar besar.
- Tidak ada tombol dekoratif yang tidak berfungsi.

## 5. Pendekatan yang dipilih

**A: rebuild UI di tempat.** Ganti widget UI dengan versi button-based sesuai referensi visual. Modul yang teruji tetap dipakai:

- `hitung/engine.py` — tokenizer + parser + evaluator.
- `hitung/format.py` — format angka Indonesia.
- `hitung/history.py` — record riwayat + recall.
- `hitung/config.py` + `hitung/storage.py` — pengaturan + riwayat JSONL.
- `hitung/theme.py` — palet + theme Textual.

Yang dibuang: `finance`, `electrical`, `math`, `date`, `data` (bin/hex) tools dan engine terkait. Yang ditulis baru: display calculator, keypad ilmiah, converter interface, numeric keypad, sidebar/dashboard.

## 6. Keputusan yang sudah disepakati

- Brand: **KALKULATOR PRO** (subjudul HITUNG tidak lagi dipakai).
- Fitur lama: dibuang. Hanya alat di PRD yang tetap.
- Penyimpanan: JSONL/`config.json`, tidak SQLite.
- Input utama: tombol. Keyboard tetap alternatif (keybinding dipetakan, bukan teks bebas).
- Desain visual mengikuti referensi gambar (dark navy, rounded button, panel slate).

### 6a. Jawaban dari review desain

1. **Sumber kebenaran:** PRD berada di percakapan; dokumen ini menjadi acuan lengkap. Daftar sidebar di §7 adalah daftar fitur eksklusif. Persentase (dengan mode Diskon & Pajak) tetap ada sebagai satu layar terpisah, sesuai PRD §6.
2. **Display kalkulator:** read-only. Tombol menulis ekspresi; keyboard hanya memetakan karakter ke aksi tombol. Tidak ada `Input` teks utama. Test UI ditulis ulang sesuai perilaku tombol.
3. **Persentase:** layar `Percentage` dengan mode: X% dari Y, perubahan %, Diskon, Pajak. Dipisah dari Tip.
4. **Tip:** layar terpisah (bukan tab converter), dengan layout Bill, Tip %, People, dan 4 hasil.
5. **Tombol `%`:** persentase kontekstual. Jika ekspresi mengandung `+` atau `-`, `10%` diartikan sebagai persentase dari sisi kiri (mis. `200 + 10%` = `220`). Jika tidak ada `+`/`-`, `%` membagi 100. Dihitung di lapisan UI, engine tetap `postfix /100`.
6. **Gambar referensi:** tidak ada di repo; mengikuti gambar di percakapan. Menggunakan `border: round` di TCSS untuk sudut membulat.
7. **Tombol `⇄`:** menukar ekspresi dengan hasil (ANS). **Tombol `↑`/`↓` di converter:** memindahkan fokus ke FROM / TO.

## 7. Layout target

### Sidebar (kiri, lebar ~22)
```
[Logo] KALKULATOR PRO
Dashboard
Calculator
  Standard
  Scientific
Unit Converter
  Area
  Length
  Temperature
  Volume
  Mass
  Data
  Speed
  Time
Percentage
Tip
History
Favorites
Settings
Help
```

### Dashboard (kanan atas)
- Judul "Welcome to KALKULATOR PRO" + tag v2.0.
- Search box (Ctrl+K).
- Quick Access: Scientific, Unit Converter, Percentage, Tip (kartu).
- Recent Calculations (5 terakhir, Clear All).
- Favorite Tools.

### Kalkulator Ilmiah
- Display atas: ekspresi + hasil besar + mode DEG/RAD.
- Keypad grid 7 kolom: fungsi kiri, angka tengah, operator kanan.
- Tombol: ⇄, DEG, √, C, ( ), %, ÷, sin, cos, tan, 7, 8, 9, ×, ln, log, 1/x, 4, 5, 6, −, eˣ, x², xʸ, 1, 2, 3, +, |x|, π, e, +/−, 0, ., =.

### Unit Converter
- Tab kategori horizontal: [Area][Length][Temperature][Volume][Mass][Data][Speed][Time].
- FROM panel: dropdown satuan + hasil input besar.
- Tombol SWAP.
- TO panel: dropdown satuan + hasil konversi besar.
- Numeric keypad bawah: 7,8,9,⌫ / 4,5,6,C / 1,2,3,↑ / +/−,0,.,↓.
- Hasil konversi diperbarui otomatis.

### Percentage
- Mode: X% dari Y, Perubahan %, Diskon, Pajak.
- Input nilai + tombol Hitung.
- Output deskriptif.

### Tip Calculator
- Bill Amount.
- Tip Percentage: quick 5%, 10%, 15%, 20%, Custom.
- Number of People: −, +.
- Output: Tip Amount, Total Bill, Per Person, Tip per Person.

## 8. Warna

| Elemen | Hex |
|---|---|
| Background | #0B0E14 |
| Main panel | #111827 |
| Secondary panel | #1A202B |
| Border | #2A3444 |
| Primary text | #E6EDF3 |
| Muted text | #93A1B3 |
| Primary accent | #4C8DFF |
| Result | #6FD3A8 |
| Clear | #FF7A6B |

## 9. Yang tersisa untuk pembuatan

- Struktur file: modul `screens/`, `widgets/`, `core/` mengikuti PRD §10.
- Perencanaan tugas, test, dan urutan implementasi (fase P0 lalu P1).