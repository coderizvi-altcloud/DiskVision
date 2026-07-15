import sys
from colorama import Fore, Style
from core.constants import MAX_PATH_DISPLAY, HASH_PROGRESS_INTERVAL, HASH_PROGRESS_BAR_LEN
from core.formatter import format_size, progress_bar


def display_progress(file_count, total_bytes, elapsed):
    speed_str = ""
    if file_count > 0 and elapsed > 0:
        rate = file_count / elapsed
        speed_str = f"{rate:.0f} files/s"
    sys.stdout.write(
        f"\r  {Fore.CYAN}Scanning{Style.RESET_ALL} "
        f"{Fore.GREEN}{file_count:,}{Style.RESET_ALL} files | "
        f"{Fore.YELLOW}{format_size(total_bytes)}{Style.RESET_ALL} | "
        f"{Fore.WHITE}{speed_str}{Style.RESET_ALL}   "
    )
    sys.stdout.flush()


def display_hash_progress(done, total):
    if total > 0 and done % HASH_PROGRESS_INTERVAL == 0:
        pct = done / total * 100
        sys.stdout.write(
            f"\r  {Fore.CYAN}Hashing{Style.RESET_ALL} "
            f"{progress_bar(pct, HASH_PROGRESS_BAR_LEN)} "
            f"{Fore.GREEN}{done}{Style.RESET_ALL}/{Fore.WHITE}{total}{Style.RESET_ALL} groups   "
        )
        sys.stdout.flush()


def show_summary(target_path, count, total_bytes, interrupted):
    lines = []
    lines.append(f"{Fore.WHITE}  Directory : {Fore.YELLOW}{target_path}{Style.RESET_ALL}")
    lines.append(f"{Fore.WHITE}  Total     : {Fore.GREEN}{count:,} files{Style.RESET_ALL} ({format_size(total_bytes)})")
    if interrupted:
        lines.append(f"{Fore.RED}  * Scan was interrupted - showing partial results{Style.RESET_ALL}")
    lines.append("")
    return lines


def show_top_files(top_files, top_n):
    lines = []
    for i, entry in enumerate(top_files[:top_n], 1):
        size_str = format_size(entry.size)
        if len(entry.path) > MAX_PATH_DISPLAY:
            display = "..." + entry.path[-(MAX_PATH_DISPLAY - 3):]
        else:
            display = entry.path
        lines.append(f"{Fore.WHITE}  {i:2d}. {Fore.GREEN}{size_str:>10}{Style.RESET_ALL} {Fore.CYAN}{display}{Style.RESET_ALL}")
    return lines


def show_type_stats(type_stats, total_bytes):
    if not type_stats:
        return
    print()
    print(f"  {Fore.WHITE}File Type Statistics:{Style.RESET_ALL}")
    sorted_types = sorted(type_stats.items(), key=lambda x: x[1]["bytes"], reverse=True)
    for cat, info in sorted_types:
        pct = (info["bytes"] / total_bytes * 100) if total_bytes > 0 else 0
        print(f"    {Fore.GREEN}{cat:<14}{Style.RESET_ALL} {info['count']:>6} files  {format_size(info['bytes']):>10}  ({pct:.1f}%)")


def show_folder_stats(folder_sizes):
    if not folder_sizes:
        return
    print()
    print(f"  {Fore.WHITE}Largest Folders:{Style.RESET_ALL}")
    top_folders = sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:10]
    for folder, size in top_folders:
        short = folder if len(folder) <= 50 else "..." + folder[-47:]
        print(f"    {Fore.YELLOW}{format_size(size):>10}{Style.RESET_ALL}  {Fore.CYAN}{short}{Style.RESET_ALL}")


def show_menu():
    print()
    print(f"  {Fore.WHITE}Actions:{Style.RESET_ALL}")
    print(f"    {Fore.GREEN}[E]{Style.RESET_ALL} Export to CSV  {Fore.GREEN}[J]{Style.RESET_ALL} Export to JSON  {Fore.GREEN}[D]{Style.RESET_ALL} Show duplicates  {Fore.GREEN}[Enter]{Style.RESET_ALL} Exit")
    return input(f"  {Fore.GREEN}>{Style.RESET_ALL} ").strip().lower()


def display_results(top_files, count, total_bytes, type_stats, folder_sizes, duplicates, target_path, top_n, interrupted, skipped_files):
    from core.formatter import clear, draw_box

    clear()
    print()

    summary_lines = show_summary(target_path, count, total_bytes, interrupted)
    top_lines = show_top_files(top_files, top_n)
    draw_box(summary_lines + top_lines, "DISK INFOGETTER - RESULTS")

    show_type_stats(type_stats, total_bytes)
    show_folder_stats(folder_sizes)

    if duplicates:
        print()
        print(f"  {Fore.YELLOW}Duplicates: {len(duplicates)} files{Style.RESET_ALL}")

    if skipped_files:
        print()
        print(f"  {Fore.RED}Skipped {len(skipped_files)} files (permission errors){Style.RESET_ALL}")

    return show_menu()


def show_duplicates(duplicates):
    from core.formatter import clear, draw_box

    clear()
    print()
    lines = [f"{Fore.WHITE}  Found {Fore.YELLOW}{len(duplicates)}{Style.RESET_ALL}{Fore.WHITE} duplicate files{Style.RESET_ALL}", ""]
    for dup_path, original, size in duplicates[:30]:
        short_dup = dup_path if len(dup_path) <= 44 else "..." + dup_path[-41:]
        lines.append(f"{Fore.GREEN}{format_size(size):>10}{Style.RESET_ALL} {Fore.CYAN}{short_dup}{Style.RESET_ALL}")
    draw_box(lines, "DUPLICATES")
    print()
    input(f"  {Fore.WHITE}Press Enter to go back...{Style.RESET_ALL}")
