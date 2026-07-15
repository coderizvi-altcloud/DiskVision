import os
import sys
from colorama import Fore, Style
from core.constants import (
    WIDTH, BOX_EMPTY_ROWS, PROGRESS_BAR_LEN, SIZE_UNITS, FILE_TYPES,
)


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


def draw_box(lines, title=""):
    top = "=" * WIDTH
    print(Fore.WHITE + top)
    if title:
        padding = (WIDTH - len(title) - 4) // 2
        rpad = WIDTH - padding - len(title) - 4
        if rpad < 0:
            rpad = 0
        print(Fore.WHITE + "=" + " " * max(0, padding) + f"[ {title} ]" + " " * rpad + "=")
        print(Fore.WHITE + "=" * WIDTH)
    for line in lines:
        visible_len = len(line.replace(Fore.WHITE, "").replace(Fore.GREEN, "").replace(Fore.CYAN, "").replace(Fore.YELLOW, "").replace(Fore.RED, "").replace(Style.RESET_ALL, ""))
        padding = WIDTH - 4 - visible_len
        if padding < 0:
            padding = 0
        print(Fore.WHITE + "|| " + line + " " * padding + Fore.WHITE + "||")
    remaining = BOX_EMPTY_ROWS - len(lines)
    for _ in range(max(0, remaining)):
        print(Fore.WHITE + "||" + " " * (WIDTH - 2) + "||")
    print(Fore.WHITE + "=" * WIDTH)
    print(Fore.WHITE + "=" * WIDTH + Style.RESET_ALL)


def format_size(size_bytes):
    for unit, divisor in SIZE_UNITS:
        if size_bytes >= divisor:
            return f"{size_bytes / divisor:.2f} {unit}"
    return f"{size_bytes} B"


def get_file_category(ext):
    ext_lower = ext.lower()
    for category, extensions in FILE_TYPES.items():
        if ext_lower in extensions:
            return category
    return "Other"


def progress_bar(pct, bar_len=PROGRESS_BAR_LEN):
    filled = int(bar_len * pct / 100)
    bar = "█" * filled + "░" * (bar_len - filled)
    return f"[{bar}] {pct:.1f}%"
