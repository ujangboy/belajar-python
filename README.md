# 01_Belajar_python

Belajar dasar-dasar pemrograman Python.

## Isi

- `01_Materi_Dasar` — materi dasar Python
- `02_Latihan` — latihan soal dan praktik
- `03_Mini_Projects` — proyek mini
- `belajar ML` — pengenalan machine learning
- `coretan.py` / `coretanjp.ipynb` — catatan eksperimen

## Virtual Environment (venv)

Project ini sudah memiliki environment virtual di folder `.venv`. Gunanya agar package dan dependency project tetap terisolasi dari Python global di komputer.

### 1. Membuat venv baru

Jika folder `.venv` belum ada, jalankan:

```bash
cd /home/a7916/Projects/belajar-python
python3 -m venv .venv
```

### 2. Mengaktifkan venv

Di Linux/macOS:

```bash
cd /home/a7916/Projects/belajar-python
source .venv/bin/activate
```

Di Windows PowerShell:

```powershell
cd C:\path\ke\belajar-python
.\.venv\Scripts\Activate.ps1
```

Di Windows Command Prompt:

```cmd
cd C:\path\ke\belajar-python
.venv\Scripts\activate.bat
```

Setelah aktif, prompt terminal biasanya berubah menjadi seperti:

```bash
(.venv) user@pc:~/Projects/belajar-python$
```

### 3. Mengecek Python dan pip yang aktif

```bash
python --version
pip --version
```

### 4. Menginstall dependency

Contoh install package:

```bash
pip install requests
```

Atau jika punya file requirements:

```bash
pip install -r requirements.txt
```

### 5. Menyimpan dependency

```bash
pip freeze > requirements.txt
```

### 6. Menonaktifkan venv

```bash
deactivate
```

### 7. Cara kerja venv di project ini

- package dipasang di folder `.venv`
- project tetap rapi dan tidak mencampur dependency global
- setiap project bisa punya versi Python/package yang berbeda

## Cara Menjalankan Program

```bash
python3 coretan.py
```

Jika sudah aktif di venv:

```bash
python coretan.py
```

## Teknologi

- Python 3
- Jupyter Notebook
- Virtual Environment (`venv`)

## Tips

- Jangan commit folder `.venv` ke Git jika tidak diinginkan.
- Pastikan selalu aktifkan venv sebelum install package atau menjalankan script.
- Gunakan `pip freeze` untuk melihat dependency yang dipakai saat ini.