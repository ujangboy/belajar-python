#!/usr/bin/env python3
"""
🚀 System Info Keren — Terminal Linux
Menampilkan informasi sistem dengan gaya futuristik + animasi
"""

import os
import sys
import time
import platform
import shutil
import psutil
import subprocess
import json
from datetime import datetime

# ─── ANSI COLORS ───────────────────────────────────────────────
class Warna:
    """Palet warna ANSI biar gampang dipanggil"""
    RESET   = '\033[0m'
    BOLD    = '\033[1m'
    DIM     = '\033[2m'
    ITALIC  = '\033[3m'
    BLINK   = '\033[5m'
    
    # Foreground
    HIJAU   = '\033[38;5;46m'
    CYAN    = '\033[38;5;51m'
    MERAH   = '\033[38;5;196m'
    KUNING  = '\033[38;5;226m'
    UNGU    = '\033[38;5;141m'
    PINK    = '\033[38;5;213m'
    PUTIH   = '\033[38;5;255m'
    ABU     = '\033[38;5;244m'
    BIRU    = '\033[38;5;39m'
    OREN    = '\033[38;5;214m'
    
    # Background
    BG_HIJAU  = '\033[48;5;46m'
    BG_CYAN   = '\033[48;5;51m'
    BG_UNGU   = '\033[48;5;141m'
    BG_MERAH  = '\033[48;5;196m'
    BG_ABU    = '\033[48;5;240m'


# ─── FUNGSI HELPER ─────────────────────────────────────────────

def bersih():
    os.system('cls' if os.name == 'nt' else 'clear')

def ukuran_terminal():
    """Dapatkan lebar & tinggi terminal"""
    cols, rows = shutil.get_terminal_size()
    return cols, rows

def gradient_text(teks, warna_mulai, warna_akhir):
    """Buat teks gradient sederhana (2 warna)"""
    return f"{warna_mulai}{teks}{warna_akhir}"

def progress_bar(persen, panjang=20):
    """Buat progress bar keren"""
    terisi = int(panjang * persen / 100)
    kosong = panjang - terisi
    bar = '█' * terisi + '░' * kosong
    return bar

def baca_file(path):
    """Baca file, return None kalo error"""
    try:
        with open(path, 'r') as f:
            return f.read().strip()
    except:
        return None

# ─── PENGUMPUL DATA SISTEM ────────────────────────────────────

class SistemInfo:
    """Kumpulin semua data sistem"""
    
    @staticmethod
    def hostname():
        return platform.node()
    
    @staticmethod
    def username():
        return os.getenv('USER') or os.getenv('USERNAME') or 'unknown'
    
    @staticmethod
    def os_info():
        os_name = platform.system()
        os_versi = platform.release()
        if os_name == 'Linux':
            # Coba dapatkan nama distro
            os_info = baca_file('/etc/os-release')
            if os_info:
                for line in os_info.split('\n'):
                    if line.startswith('PRETTY_NAME='):
                        return line.split('=')[1].strip('"')
        return f"{os_name} {os_versi}"
    
    @staticmethod
    def kernel():
        return platform.release()
    
    @staticmethod
    def uptime():
        try:
            with open('/proc/uptime', 'r') as f:
                uptime_detik = float(f.read().split()[0])
            hari = int(uptime_detik // 86400)
            jam = int((uptime_detik % 86400) // 3600)
            menit = int((uptime_detik % 3600) // 60)
            if hari > 0:
                return f"{hari}h {jam}j {menit}m"
            return f"{jam}j {menit}m"
        except:
            return "N/A"
    
    @staticmethod
    def cpu_info():
        try:
            model = baca_file('/proc/cpuinfo')
            if model:
                for line in model.split('\n'):
                    if 'model name' in line:
                        nama = line.split(':')[1].strip()
                        # Persingkat biar keren
                        if 'Intel' in nama:
                            nama = nama.replace('(R)', '®').replace('(TM)', '™')
                            # Ambil bagian penting aja
                            parts = nama.split()
                            if len(parts) > 4:
                                nama = ' '.join(parts[:3]) + ' ' + parts[-1]
                        return nama
            return platform.processor() or "N/A"
        except:
            return "N/A"
    
    @staticmethod
    def cpu_count():
        return os.cpu_count() or 0
    
    @staticmethod
    def cpu_percent():
        return psutil.cpu_percent(interval=0.3)
    
    @staticmethod
    def cpu_temp():
        try:
            temp = baca_file('/sys/class/thermal/thermal_zone0/temp')
            if temp:
                return f"{int(temp) / 1000:.1f}°C"
        except:
            pass
        return "N/A"
    
    @staticmethod
    def ram_info():
        mem = psutil.virtual_memory()
        total_gb = mem.total / (1024**3)
        used_gb = mem.used / (1024**3)
        return {
            'total': f"{total_gb:.1f} GB",
            'used': f"{used_gb:.1f} GB",
            'free': f"{mem.available / (1024**3):.1f} GB",
            'percent': mem.percent
        }
    
    @staticmethod
    def disk_info():
        try:
            usage = shutil.disk_usage('/')
            total_gb = usage.total / (1024**3)
            used_gb = usage.used / (1024**3)
            free_gb = usage.free / (1024**3)
            percent = (usage.used / usage.total) * 100
            return {
                'total': f"{total_gb:.1f} GB",
                'used': f"{used_gb:.1f} GB",
                'free': f"{free_gb:.1f} GB",
                'percent': percent
            }
        except:
            return {'total': 'N/A', 'used': 'N/A', 'free': 'N/A', 'percent': 0}
    
    @staticmethod
    def shell():
        return os.path.basename(os.getenv('SHELL', 'unknown'))
    
    @staticmethod
    def desktop_env():
        return os.getenv('XDG_CURRENT_DESKTOP') or os.getenv('DESKTOP_SESSION') or 'N/A'
    
    @staticmethod
    def packages():
        """Coba deteksi jumlah paket terinstall"""
        methods = [
            ('dpkg', 'dpkg --get-selections | wc -l'),
            ('rpm', 'rpm -qa | wc -l'),
            ('pacman', 'pacman -Q | wc -l'),
        ]
        for name, cmd in methods:
            try:
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    count = result.stdout.strip()
                    return f"{count} ({name})"
            except:
                continue
        return "N/A"
    
    @staticmethod
    def ip_lokal():
        try:
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=2)
            ip = result.stdout.strip().split()[0] if result.stdout.strip() else 'N/A'
            return ip
        except:
            return 'N/A'
    
    @staticmethod
    def python_version():
        return sys.version.split()[0]
    
    @staticmethod
    def terminal_emu():
        return os.getenv('TERM_PROGRAM') or os.getenv('TERM', 'unknown')
    
    @staticmethod
    def resolusi():
        cols, rows = ukuran_terminal()
        return f"{cols}x{rows}"
    
    @staticmethod
    def load_avg():
        try:
            load = os.getloadavg()
            return f"{load[0]:.2f} {load[1]:.2f} {load[2]:.2f}"
        except:
            return "N/A"
    
    @staticmethod
    def proses_count():
        return len(psutil.pids())


# ─── RENDER TAMPILAN ──────────────────────────────────────────

def bingkai_atas(lebar):
    """Bingkai atas dengan aksen"""
    print(f"{Warna.CYAN}╭{'─' * (lebar - 2)}╮{Warna.RESET}")

def bingkai_bawah(lebar):
    """Bingkai bawah dengan aksen"""
    print(f"{Warna.CYAN}╰{'─' * (lebar - 2)}╯{Warna.RESET}")

def tulis_baris(teks, warna=Warna.PUTIH, rata='kiri', lebar=None):
    """Tulis baris dengan padding"""
    if lebar is None:
        lebar, _ = ukuran_terminal()
    isi = lebar - 4  # 2 border + 2 spasi
    if rata == 'tengah':
        kiri = (isi - len(teks)) // 2
        kanan = isi - len(teks) - kiri
        print(f"{Warna.CYAN}│{Warna.RESET} {' ' * kiri}{warna}{teks}{Warna.RESET}{' ' * kanan} {Warna.CYAN}│{Warna.RESET}")
    else:
        teks_trunc = teks[:isi] if len(teks) > isi else teks
        padding = isi - len(teks_trunc)
        print(f"{Warna.CYAN}│{Warna.RESET} {warna}{teks_trunc}{' ' * padding} {Warna.CYAN}│{Warna.RESET}")

def tulis_label_nilai(label, nilai, warna_label=Warna.ABU, warna_nilai=Warna.PUTIH, lebar=None):
    """Tulis baris dengan format label: nilai"""
    if lebar is None:
        lebar, _ = ukuran_terminal()
    isi = lebar - 4
    teks = f"{warna_label}{label}:{Warna.RESET} {warna_nilai}{nilai}{Warna.RESET}"
    teks_plain = f"{label}: {nilai}"
    if len(teks_plain) > isi:
        teks_plain = teks_plain[:isi]
        teks = f"{warna_label}{label}:{Warna.RESET} {warna_nilai}{nilai[:isi - len(label) - 2]}{Warna.RESET}"
    padding = isi - len(teks_plain)
    print(f"{Warna.CYAN}│{Warna.RESET} {teks}{' ' * padding} {Warna.CYAN}│{Warna.RESET}")


def tampilkan_logo_ascii():
    """Tampilkan logo ASCII keren"""
    logo = f"""
{Warna.MERAH}    ██╗  ██╗███████╗██████╗ ███╗   ██╗██╗
{Warna.KUNING}    ██║  ██║██╔════╝██╔══██╗████╗  ██║██║
{Warna.HIJAU}    ███████║█████╗  ██████╔╝██╔██╗ ██║██║
{Warna.CYAN}    ██╔══██║██╔══╝  ██╔══██╗██║╚██╗██║██║
{Warna.UNGU}    ██║  ██║███████╗██║  ██║██║ ╚████║███████╗
{Warna.PINK}    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝{Warna.RESET}
    """
    return logo


def tampilkan_info_sistem():
    """Main function: tampilkan semua info sistem"""
    info = SistemInfo()
    lebar, _ = ukuran_terminal()
    lebar = min(lebar, 80)  # Maks 80 biar rapi
    
    bersih()
    
    # ── HEADER ──
    bingkai_atas(lebar)
    tulis_baris("", lebar=lebar)
    
    # Logo + salam
    salam = f"Halo, {Warna.PINK}{info.username()}{Warna.RESET}! Selamat datang di {Warna.CYAN}{info.hostname()}{Warna.RESET}"
    tulis_baris(salam, rata='tengah', lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    # Waktu
    now = datetime.now().strftime("%A, %d %B %Y  %H:%M:%S")
    tulis_baris(f"🕐  {now}", warna=Warna.KUNING, rata='tengah', lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    bingkai_bawah(lebar)
    
    # ── SISTEM ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"  {Warna.BOLD}{Warna.CYAN}⚙️  SISTEM{Warna.RESET}", lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    tulis_label_nilai("OS", info.os_info(), warna_nilai=Warna.HIJAU, lebar=lebar)
    tulis_label_nilai("Kernel", info.kernel(), warna_nilai=Warna.CYAN, lebar=lebar)
    tulis_label_nilai("Uptime", info.uptime(), warna_nilai=Warna.KUNING, lebar=lebar)
    tulis_label_nilai("Shell", info.shell(), warna_nilai=Warna.PINK, lebar=lebar)
    tulis_label_nilai("DE/WM", info.desktop_env(), warna_nilai=Warna.UNGU, lebar=lebar)
    tulis_label_nilai("Terminal", info.terminal_emu(), warna_nilai=Warna.OREN, lebar=lebar)
    tulis_label_nilai("Resolusi", info.resolusi(), warna_nilai=Warna.ABU, lebar=lebar)
    tulis_label_nilai("Paket", info.packages(), warna_nilai=Warna.HIJAU, lebar=lebar)
    tulis_baris("", lebar=lebar)
    bingkai_bawah(lebar)
    
    # ── CPU ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"  {Warna.BOLD}{Warna.MERAH}🔥  CPU{Warna.RESET}", lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    cpu_model = info.cpu_info()
    tulis_label_nilai("Model", cpu_model, warna_nilai=Warna.MERAH, lebar=lebar)
    tulis_label_nilai("Core", f"{info.cpu_count()} thread", warna_nilai=Warna.KUNING, lebar=lebar)
    tulis_label_nilai("Suhu", info.cpu_temp(), warna_nilai=Warna.OREN, lebar=lebar)
    
    cpu_percent = info.cpu_percent()
    bar = progress_bar(cpu_percent)
    warna_bar = Warna.HIJAU if cpu_percent < 50 else (Warna.KUNING if cpu_percent < 80 else Warna.MERAH)
    tulis_label_nilai("Load", f"{warna_bar}{bar}{Warna.RESET} {cpu_percent:.1f}%", warna_nilai='', lebar=lebar)
    tulis_label_nilai("Avg", info.load_avg(), warna_nilai=Warna.ABU, lebar=lebar)
    tulis_baris("", lebar=lebar)
    bingkai_bawah(lebar)
    
    # ── RAM ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"  {Warna.BOLD}{Warna.HIJAU}💾  MEMORI{Warna.RESET}", lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    ram = info.ram_info()
    tulis_label_nilai("Total", ram['total'], warna_nilai=Warna.CYAN, lebar=lebar)
    tulis_label_nilai("Used", ram['used'], warna_nilai=Warna.KUNING, lebar=lebar)
    tulis_label_nilai("Free", ram['free'], warna_nilai=Warna.HIJAU, lebar=lebar)
    
    bar_ram = progress_bar(ram['percent'])
    warna_ram = Warna.HIJAU if ram['percent'] < 50 else (Warna.KUNING if ram['percent'] < 80 else Warna.MERAH)
    tulis_label_nilai("Usage", f"{warna_ram}{bar_ram}{Warna.RESET} {ram['percent']:.1f}%", warna_nilai='', lebar=lebar)
    tulis_baris("", lebar=lebar)
    bingkai_bawah(lebar)
    
    # ── DISK ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"  {Warna.BOLD}{Warna.KUNING}📀  PENYIMPANAN{Warna.RESET}", lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    disk = info.disk_info()
    tulis_label_nilai("Total", disk['total'], warna_nilai=Warna.CYAN, lebar=lebar)
    tulis_label_nilai("Used", disk['used'], warna_nilai=Warna.KUNING, lebar=lebar)
    tulis_label_nilai("Free", disk['free'], warna_nilai=Warna.HIJAU, lebar=lebar)
    
    bar_disk = progress_bar(disk['percent'])
    warna_disk = Warna.HIJAU if disk['percent'] < 50 else (Warna.KUNING if disk['percent'] < 80 else Warna.MERAH)
    tulis_label_nilai("Usage", f"{warna_disk}{bar_disk}{Warna.RESET} {disk['percent']:.1f}%", warna_nilai='', lebar=lebar)
    tulis_baris("", lebar=lebar)
    bingkai_bawah(lebar)
    
    # ── JARINGAN & PROSES ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"  {Warna.BOLD}{Warna.UNGU}🌐  LAINNYA{Warna.RESET}", lebar=lebar)
    tulis_baris("", lebar=lebar)
    
    tulis_label_nilai("IP Lokal", info.ip_lokal(), warna_nilai=Warna.CYAN, lebar=lebar)
    tulis_label_nilai("Proses", f"{info.proses_count()} running", warna_nilai=Warna.KUNING, lebar=lebar)
    tulis_label_nilai("Python", info.python_version(), warna_nilai=Warna.HIJAU, lebar=lebar)
    tulis_baris("", lebar=lebar)
    bingkai_bawah(lebar)
    
    # ── FOOTER ──
    print()
    bingkai_atas(lebar)
    tulis_baris(f"{Warna.DIM}  ⚡  Generated with ❤️  using Python  ⚡{Warna.RESET}", rata='tengah', lebar=lebar)
    bingkai_bawah(lebar)
    print()


# ─── ANIMASI LOADING ──────────────────────────────────────────

def animasi_loading(detik=1.5):
    """Animasi loading sederhana"""
    chars = '⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏'
    lebar, _ = ukuran_terminal()
    lebar = min(lebar, 80)
    
    for i in range(int(detik * 10)):
        ch = chars[i % len(chars)]
        msg = f"{Warna.CYAN}{ch}{Warna.RESET} {Warna.ABU}Mengumpulkan data sistem...{Warna.RESET}"
        padding = lebar - len(msg) + 20  # +20 buat ANSI
        print(f"\r{' ' * (padding // 2)}{msg}", end='', flush=True)
        time.sleep(0.1)
    print()


# ─── MAIN ─────────────────────────────────────────────────────

if __name__ == '__main__':
    try:
        # Cek dependencies
        try:
            import psutil
        except ImportError:
            print(f"{Warna.MERAH}⚠️  psutil belum terinstall. Install dulu:{Warna.RESET}")
            print(f"  {Warna.KUNING}pip install psutil{Warna.RESET}")
            sys.exit(1)
        
        animasi_loading(1.2)
        tampilkan_info_sistem()
        
    except KeyboardInterrupt:
        print(f"\n{Warna.KUNING}⚠️  Dibatalakan.{Warna.RESET}")
        sys.exit(0)