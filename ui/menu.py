from core.constants import DEFAULT_TOP_N
from core.formatter import clear, draw_box
from core.scanner import Scanner
from ui.display import display_results, show_duplicates
from exporters.csv_export import export_csv
from exporters.json_export import export_json
from colorama import Fore


def interactive_menu():
    scanner = Scanner()

    clear()
    print()
    lines = [
        "",
        f"{Fore.WHITE}  This tool scans for files and displays the{Style.RESET_ALL}",
        f"{Fore.WHITE}  largest ones sorted by size with stats.{Style.RESET_ALL}",
        "",
        f"{Fore.WHITE}  Supports filtering, duplicates, export & more{Style.RESET_ALL}",
        "",
    ]
    draw_box(lines, "DISK INFOGETTER")
    print()
    target = input(f"  {Fore.GREEN}Path to scan >{Style.RESET_ALL} ").strip()
    if not target:
        target = "E:\\"

    ext_input = input(f"  {Fore.GREEN}File extensions (comma sep, or Enter for all) >{Style.RESET_ALL} ").strip()
    extensions = None
    if ext_input:
        extensions = set("." + e.strip().lstrip(".").lower() for e in ext_input.split(","))

    min_size_input = input(f"  {Fore.GREEN}Min size in MB (Enter to skip) >{Style.RESET_ALL} ").strip()
    min_size = 0
    if min_size_input:
        try:
            min_size = int(min_size_input) * 1024 * 1024
        except ValueError:
            min_size = 0

    max_size_input = input(f"  {Fore.GREEN}Max size in MB (Enter to skip) >{Style.RESET_ALL} ").strip()
    max_size = None
    if max_size_input:
        try:
            max_size = int(max_size_input) * 1024 * 1024
        except ValueError:
            max_size = None

    search_input = input(f"  {Fore.GREEN}Search filename (Enter to skip) >{Style.RESET_ALL} ").strip()
    search_name = search_input if search_input else None

    top_n_input = input(f"  {Fore.GREEN}How many top files to show [{DEFAULT_TOP_N}] >{Style.RESET_ALL} ").strip()
    top_n = DEFAULT_TOP_N
    if top_n_input:
        try:
            top_n = int(top_n_input)
        except ValueError:
            top_n = DEFAULT_TOP_N

    clear()
    print()
    lines = [
        "",
        f"{Fore.WHITE}  Target: {Fore.YELLOW}{target}{Style.RESET_ALL}",
        f"{Fore.WHITE}  Scanning... please wait{Style.RESET_ALL}",
        "",
    ]
    draw_box(lines, "LOADING")
    print()

    top_files, count, total_bytes, type_stats, folder_sizes, duplicates = scanner.scan_files(
        target, extensions, min_size, max_size, search_name, top_n
    )

    if top_files is None:
        clear()
        print()
        lines = [
            "",
            f"{Fore.RED}  ERROR: Directory not found or not accessible{Style.RESET_ALL}",
            f"{Fore.WHITE}  Path: {Fore.YELLOW}{target}{Style.RESET_ALL}",
            "",
        ]
        draw_box(lines, "ERROR")
        print()
        input(f"  {Fore.WHITE}Press Enter to exit...{Style.RESET_ALL}")
        return

    while True:
        choice = display_results(
            top_files, count, total_bytes, type_stats, folder_sizes,
            duplicates, target, top_n, scanner.interrupted, scanner.skipped_files,
        )

        if choice == "e":
            export_csv(top_files, type_stats, folder_sizes, duplicates, target, count, total_bytes)
            input(f"  {Fore.WHITE}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == "j":
            export_json(top_files, type_stats, folder_sizes, duplicates, target, count, total_bytes)
            input(f"  {Fore.WHITE}Press Enter to continue...{Style.RESET_ALL}")
        elif choice == "d":
            if duplicates:
                show_duplicates(duplicates)
            else:
                print(f"  {Fore.GREEN}No duplicates found.{Style.RESET_ALL}")
                input(f"  {Fore.WHITE}Press Enter to continue...{Style.RESET_ALL}")
        else:
            break
