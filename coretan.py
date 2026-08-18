# Wrote ultah_yasmin.py
import pyfiglet
from termcolor import colored
import random
import time
import os
import sys
import shutil
import unicodedata
import threading
import math

# --- FUNGSI HELPER UNTUK CENTERING AKURAT (WSL SAFE) ---
def get_visual_width(text):
    """Menghitung lebar visual string yang akurat untuk Terminal (Emoji = 2 width)"""
    width = 0
    for char in text:
        if unicodedata.east_asian_width(char) in ('F', 'W'):
            width += 2
        else:
            width += 1
    return width

def center_text_visual(text, total_width):
    """Menengahkan teks berdasarkan lebar visual aktual, bukan len() python"""
    visual_len = get_visual_width(text)
    if visual_len >= total_width:
        return text
    padding = total_width - visual_len
    left_pad = padding // 2
    right_pad = padding - left_pad
    return (' ' * left_pad) + text + (' ' * right_pad)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def hide_cursor():
    sys.stdout.write('\033[?25l')
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write('\033[?25h')
    sys.stdout.flush()

def move_cursor(row, col):
    sys.stdout.write(f"\033[{row};{col}H")

def rainbow_color(t, offset=0.0):
    """Mengembalikan warna romantis berdasarkan fase waktu (siklus merah→pink→emas→ungu)"""
    phase = (t + offset) % 1.0
    if phase < 0.25:
        return 'red'
    elif phase < 0.5:
        return 'magenta'
    elif phase < 0.75:
        return 'yellow'
    else:
        return 'light_magenta'

def selamat_ulang_tahun_hamida():
    hide_cursor()
    clear_screen()
    cols, rows = shutil.get_terminal_size((80, 24))

    lope_variants = ['💖', '💕', '💗', '💘', '❤️', '🩷']
    warna_hujan = ['red', 'magenta', 'light_red', 'light_magenta', 'yellow', 'white']

    # === 0. INTRO DRAMATIS: HEARTBEAT (DETAK JANTUNG) ===
    print("\n")
    print(center_text_visual("a little something... for you 🤍", cols), end="\r")
    sys.stdout.flush()
    time.sleep(1.2)

    beat_chars = ['♡', '♥', '❤', '♥']
    intro_lines = (rows - 6) // 2
    for cycle in range(3):
        for i, ch in enumerate(beat_chars):
            clear_screen()
            print("\n" * intro_lines)
            beat_size = 1 + (i / (len(beat_chars) - 1)) * 2
            heart = colored(ch * int(beat_size), 'light_red', attrs=['bold'])
            msg = colored("my heart beats for you...", 'light_magenta', attrs=['bold'])
            print(center_text_visual(heart + "  " + msg, cols))
            sys.stdout.flush()
            time.sleep(0.18)
    time.sleep(0.5)

    # === 1. ANIMASI HUJAN CINTA YANG LEBIH LEMBUT (4 detik) ===
    clear_screen()
    print("\n")
    print(colored(center_text_visual("Falling in love for you...", cols), 'light_red', attrs=['bold']))
    print()

    durasi_hujan = 4.0 
    start_time_hujan = time.time()
    while time.time() - start_time_hujan < durasi_hujan:
        baris_hujan = [' '] * cols
        jumlah_lope = random.randint(6, 12)
        for _ in range(jumlah_lope):
            pos = random.randint(0, cols - 2)
            baris_hujan[pos] = random.choice(lope_variants)
        line_str = ''.join(baris_hujan)
        print(colored(line_str, random.choice(warna_hujan)), end='\r')
        sys.stdout.flush()
        time.sleep(0.08)
        print()
    time.sleep(0.3)

    # === 2. SETUP UNTUK ASCII ART & BUNGA JATUH BERSAMAAN ===
    clear_screen()
    vertical_padding = (rows - 15) // 2
    if vertical_padding > 0:
        print("\n" * vertical_padding)

    pesan_ascii = pyfiglet.figlet_format("Selamat Ulang Tahun\nCintaku Hamida")

    lines = pesan_ascii.split("\n")
    while lines and not lines[-1].strip():
        lines.pop()

    total_lines = len(lines)
    pesan_bawah = "💖✨ Wishing my dearest Hamida a day filled with joy and love! ✨💖"

    area_teks_atas = vertical_padding
    area_teks_bawah = vertical_padding + total_lines + 6
    area_teks_tengah_kiri = (cols // 2) - 24
    area_teks_tengah_kanan = (cols // 2) + 24

    # Bintang berkedip di background
    bunga_emoji = ['🌸', '🌹', '🌺', '🌷', '💐', '🥀', '💖', '💕', '💗', '💘', '❤️', '🩷', '✨', '⭐', '💫', '🌟']
    warna_bunga = ['red', 'magenta', 'light_red', 'light_magenta', 'yellow', 'white', 'light_yellow', 'light_cyan']
    bintang_emoji = ['✦', '✧', '⋆', '·', '✩']

    lebar_zona_kiri = 10
    lebar_zona_kanan = 10
    zona_kiri = list(range(0, min(lebar_zona_kiri, cols // 2)))
    zona_kanan = list(range(max(0, cols - lebar_zona_kanan), cols - 1))
    semua_zona_kolom = zona_kiri + zona_kanan

    animasi_berjalan = True
    bunga_list = []
    bintang_list = []
    for _ in range(int(cols * 0.4)):
        bintang_list.append({
            'row': random.randint(0, rows - 1),
            'col': random.randint(0, cols - 1),
            'ch': random.choice(bintang_emoji),
            'phase': random.random(),
        })

    def hujan_dan_bintang():
        nonlocal animasi_berjalan, bunga_list, bintang_list
        t = 0.0
        while animasi_berjalan:
            t += 0.02
            # Spawn bunga
            for _ in range(random.randint(4, 9)):
                target_col = random.choice(semua_zona_kolom)
                if area_teks_tengah_kiri < target_col < area_teks_tengah_kanan:
                    continue
                bunga_list.append({
                    'row': 0,
                    'col': target_col,
                    'emoji': random.choice(bunga_emoji),
                    'warna': random.choice(warna_bunga),
                    'drift': random.uniform(-0.3, 0.3),
                })

            bunga_baru = []
            for bunga in bunga_list:
                bunga['row'] += 1
                bunga['col'] += bunga['drift']
                c = int(round(bunga['col']))
                if 0 <= c < cols and bunga['row'] < rows and not (
                    area_teks_atas <= bunga['row'] < area_teks_bawah
                    and area_teks_tengah_kiri < c < area_teks_tengah_kanan
                ):
                    try:
                        move_cursor(bunga['row'] + 1, c + 1)
                        sys.stdout.write(colored(bunga['emoji'], bunga['warna']))
                    except:
                        pass
                    bunga_baru.append(bunga)
            bunga_list = bunga_baru

            # Bintang berkedip (twinkle)
            for b in bintang_list:
                tw = 0.5 + 0.5 * math.sin(t * 2.0 + b['phase'] * 6.28)
                if tw > 0.85:
                    try:
                        move_cursor(b['row'] + 1, b['col'] + 1)
                        sys.stdout.write(colored(b['ch'], 'light_cyan'))
                    except:
                        pass

            sys.stdout.flush()
            time.sleep(0.02)

    thread_anim = threading.Thread(target=hujan_dan_bintang)
    thread_anim.daemon = True
    thread_anim.start()

    # === 3. ASCII ART DENGAN GRADIENT BERKILAU (SHIMMER) ===
    time.sleep(0.5)
    t0 = time.time()
    for idx, baris in enumerate(lines):
        baris_centered = center_text_visual(baris, cols)
        ratio = idx / max(total_lines - 1, 1)
        if ratio < 0.33:
            warna = 'red'
        elif ratio < 0.66:
            warna = 'magenta'
        else:
            warna = 'yellow'
        print(colored(baris_centered, color=warna, attrs=['bold']), flush=True)
        time.sleep(0.18)
    time.sleep(1.2)

    # Siklus warna shimmer pada teks ASCII (2 putaran)
    for _ in range(2):
        start = time.time()
        while time.time() - start < 1.6:
            tt = time.time()
            clear_from = area_teks_atas + 1
            for i, baris in enumerate(lines):
                move_cursor(clear_from + i, 1)
                sys.stdout.write('\033[K')
            for i, baris in enumerate(lines):
                move_cursor(clear_from + i, 1)
                baris_centered = center_text_visual(baris, cols)
                wc = rainbow_color(tt / 4.0, offset=i * 0.08)
                sys.stdout.write(colored(baris_centered, color=wc, attrs=['bold']))
            sys.stdout.flush()
            time.sleep(0.05)

    # === 4. PESAN TYPEWRITER BERKILAU ===
    print("\n", end="", flush=True)
    visual_len_pesan = get_visual_width(pesan_bawah)
    left_padding = (cols - visual_len_pesan) // 2
    sys.stdout.write(' ' * left_padding)
    sys.stdout.flush()

    for ci, char in enumerate(pesan_bawah):
        wc = rainbow_color(ci * 0.05)
        sys.stdout.write(colored(char, wc, attrs=['bold']))
        sys.stdout.flush()
        time.sleep(0.045)
    print("\n\n")

    # === 5. FRAME BERCAHAYA MELINGKUP AScii ART ===
    frame_color = 'light_magenta'
    move_cursor(area_teks_atas + 1, 1)
    print(colored(center_text_visual("· · ♥ · ·  you are my forever  · · ♥ · ·", cols),
                  'light_red', attrs=['bold']), flush=True)
    time.sleep(1.0)

    # === 6. FINALE DRAMATIS ===
    animasi_berjalan = False
    thread_anim.join(timeout=0.5)
    clear_screen()

    finale_lines = pyfiglet.figlet_format("I LOVE YOU\nHAMIDA").split("\n")
    while finale_lines and not finale_lines[-1].strip():
        finale_lines.pop()
    fpad = (rows - len(finale_lines) - 4) // 2
    if fpad > 0:
        print("\n" * fpad)

    # denyut jantung pada finale
    for beat in range(4):
        scale = 1 if beat % 2 == 0 else 2
        for i, baris in enumerate(finale_lines):
            bc = center_text_visual(baris, cols)
            wc = rainbow_color(beat * 0.13, offset=i * 0.1)
            print(colored(bc, color=wc, attrs=['bold']))
        print()
        print(colored(center_text_visual("happy birthday, my love 🎂💞", cols), 'light_yellow', attrs=['bold']))
        print(colored(center_text_visual("semoga semua harapan dan impian kamu tercapai di tahun ini dan makin kecintaan sama aku :) ✨", cols), 'light_red'))
        sys.stdout.flush()
        time.sleep(0.5)
        if beat < 3:
            clear_screen()
            if fpad > 0:
                print("\n" * fpad)

    # confetti cinta terakhir
    conf = " ".join(random.choices(lope_variants + ['🌸', '✨', '🌟'], k=min(cols // 3, 25)))
    print(colored(center_text_visual(conf, cols), 'magenta', attrs=['bold']))
    print()
    show_cursor()

# Menjalankan fungsi
if __name__ == "__main__":
    try:
        selamat_ulang_tahun_hamida()
    except KeyboardInterrupt:
        show_cursor()
        clear_screen()
