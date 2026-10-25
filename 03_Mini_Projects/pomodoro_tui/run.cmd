@echo off
rem ===========================================================================
rem  FOKUS - jalankan aplikasi cukup dengan satu perintah:  run.cmd
rem
rem  Script ini:
rem   1. mencari Python yang tepat (venv repo, venv lokal proyek, atau PATH);
rem   2. memasang dependency dari requirements.txt kalau belum ada;
rem   3. menjalankan aplikasi Textual-nya.
rem
rem  Bisa dipanggil dari cmd maupun PowerShell:
rem      .\run.cmd
rem  Argumen tambahan diteruskan apa adanya ke main.py.
rem ===========================================================================
setlocal EnableExtensions
title FOKUS

rem Folder proyek = folder tempat file run.cmd ini berada (selalu diakhiri \).
set "ROOT=%~dp0"
set "PY="

rem -- 0) Pintu darurat untuk pengguna tingkat lanjut / testing --------------
if defined FOKUS_PYTHON if exist "%FOKUS_PYTHON%" set "PY=%FOKUS_PYTHON%"

rem -- 1) venv bersama di root repo:  ../../.venv ---------------------------
if not defined PY if exist "%ROOT%..\..\.venv\Scripts\python.exe" set "PY=%ROOT%..\..\.venv\Scripts\python.exe"

rem -- 2) venv lokal proyek:  ./.venv --------------------------------------
if not defined PY if exist "%ROOT%.venv\Scripts\python.exe" set "PY=%ROOT%.venv\Scripts\python.exe"

rem -- 3) python di PATH yang sudah punya textual ---------------------------
if not defined PY (
    for /f "delims=" %%I in ('where python 2^>nul') do (
        if not defined PY (
            "%%I" -c "import textual" >nul 2>nul && set "PY=%%I"
        )
    )
)

rem -- 4) py launcher yang sudah punya textual ------------------------------
if not defined PY (
    for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
        if not defined PY (
            "%%I" -c "import textual" >nul 2>nul && set "PY=%%I"
        )
    )
)

rem -- 5) python/py apa pun yang ada, nanti dependency-nya dipasang ---------
if not defined PY (
    for /f "delims=" %%I in ('where python 2^>nul') do (
        if not defined PY set "PY=%%I"
    )
)
if not defined PY (
    for /f "delims=" %%I in ('py -3 -c "import sys; print(sys.executable)" 2^>nul') do (
        if not defined PY set "PY=%%I"
    )
)

if not defined PY (
    echo.
    echo [FOKUS] Python belum ditemukan di komputer ini.
    echo.
    echo Pasang Python 3.11 atau lebih baru dari https://www.python.org/downloads/
    echo ^(centang "Add python.exe to PATH" saat instalasi^), lalu buka
    echo terminal baru dan jalankan lagi:
    echo.
    echo     run.cmd
    echo.
    exit /b 1
)

rem -- Dependency: pastikan package runtime terpasang ----------------------
"%PY%" -c "import textual" >nul 2>nul
if errorlevel 1 (
    echo [FOKUS] Dependency belum terpasang. Meng-install requirements.txt ...
    "%PY%" -m pip install -r "%ROOT%requirements.txt"
    if errorlevel 1 (
        echo.
        echo [FOKUS] Gagal memasang dependency.
        echo Pastikan komputer tersambung internet, lalu coba lagi.
        echo Kalau ingin memasang manual:
        echo.
        echo     "%PY%" -m pip install -r "%ROOT%requirements.txt"
        echo.
        exit /b 1
    )
)

rem -- Jalankan aplikasi ----------------------------------------------------
"%PY%" "%ROOT%main.py" %*
exit /b %ERRORLEVEL%
