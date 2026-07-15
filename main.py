import sys
import signal
import argparse
from core.constants import DEFAULT_TOP_N
from core.scanner import Scanner
from core.formatter import clear, draw_box
from colorama import init, Fore
from exporters.csv_export import export_csv
from exporters.json_export import export_json
from ui.display import show_summary, show_top_files
from ui.menu import interactive_menu

init()


def parse_args():
    parser = argparse.ArgumentParser(description="Disk Infogetter - Scan and analyze disk usage")
    parser.add_argument("path", nargs="?", help="Directory path to scan")
    parser.add_argument("-n", "--top", type=int, default=DEFAULT_TOP_N, help=f"Number of top files to show (default: {DEFAULT_TOP_N})")
    parser.add_argument("-e", "--extensions", help="Comma-separated file extensions to filter (e.g. .mp4,.jpg)")
    parser.add_argument("--min-size", type=int, default=0, help="Minimum file size in MB")
    parser.add_argument("--max-size", type=int, default=None, help="Maximum file size in MB")
    parser.add_argument("-s", "--search", help="Search filename substring")
    parser.add_argument("--csv", help="Export results to CSV file")
    parser.add_argument("--json", help="Export results to JSON file")
    parser.add_argument("--no-interactive", action="store_true", help="Run without interactive menu")
    parser.add_argument("--no-hash", action="store_true", help="Skip duplicate hashing")
    return parser.parse_args()


def main():
    args = parse_args()

    if args.no_interactive and args.path:
        scanner = Scanner()
        signal.signal(signal.SIGINT, lambda s, f: scanner.interrupt())

        extensions = None
        if args.extensions:
            extensions = set("." + e.strip().lstrip(".").lower() for e in args.extensions.split(","))

        min_size = args.min_size * 1024 * 1024 if args.min_size else 0
        max_size = args.max_size * 1024 * 1024 if args.max_size else None

        top_files, count, total_bytes, type_stats, folder_sizes, duplicates = scanner.scan_files(
            args.path, extensions, min_size, max_size, args.search, args.top, no_hash=args.no_hash
        )

        if top_files is None:
            print(f"Error: Directory not found: {args.path}")
            sys.exit(1)

        clear()
        print()
        summary_lines = show_summary(args.path, count, total_bytes, scanner.interrupted)
        top_lines = show_top_files(top_files, args.top)
        draw_box(summary_lines + top_lines, "DISK INFOGETTER")

        if args.csv:
            export_csv(top_files, type_stats, folder_sizes, duplicates, args.path, count, total_bytes)
        if args.json:
            export_json(top_files, type_stats, folder_sizes, duplicates, args.path, count, total_bytes)
    else:
        interactive_menu()


if __name__ == "__main__":
    main()
