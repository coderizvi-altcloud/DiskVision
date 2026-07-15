# Disk Infogetter

A fast disk usage analyzer that scans directories, finds the largest files, detects duplicates, and exports reports.

## Features

- **Fast scanning** - Uses `os.scandir()` with a single directory walk (20-40% faster than glob-based tools)
- **Duplicate detection** - Two-phase blake3 hashing: first 4KB header check, then full hash only when headers match. Threaded across CPU cores
- **Cumulative folder sizes** - Every parent directory up to the root gets the correct total size
- **Export** - CSV and JSON reports with largest files, type stats, folder sizes, and duplicates
- **Interactive menu** - Filter by extension, size range, or filename substring

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

## Installation

```bash
git clone <repo-url>
cd Disk Infogetter
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Usage

### Interactive mode

```bash
python main.py
```

You'll be prompted for:
- Path to scan (defaults to `E:\`)
- File extensions to filter (comma-separated, or Enter for all)
- Min/max file size in MB
- Filename search substring
- Number of top files to show

### Command-line mode

```bash
python main.py E:\Movies -n 50 --no-hash
```

### CLI options

| Flag | Description |
|------|-------------|
| `path` | Directory to scan |
| `-n, --top` | Number of largest files to show (default: 20) |
| `-e, --extensions` | Filter by extensions, e.g. `.mp4,.jpg` |
| `--min-size` | Minimum file size in MB |
| `--max-size` | Maximum file size in MB |
| `-s, --search` | Filename substring to search for |
| `--csv` | Export to CSV file |
| `--json` | Export to JSON file |
| `--no-interactive` | Run without interactive menu |
| `--no-hash` | Skip duplicate detection |

### Examples

Scan for largest video files:

```bash
python main.py "D:\Media" -e .mp4,.mkv,.avi -n 30
```

Find all duplicates on a drive:

```bash
python main.py E:\ --no-interactive -n 10 --csv
```

Scan only files over 100MB:

```bash
python main.py E:\ --min-size 100
```

## Project structure

```
DiskInfoGetter/
├── main.py                  # Entry point
├── core/
│   ├── constants.py         # All constants
│   ├── models.py            # FileEntry dataclass
│   ├── logger.py            # Logger setup
│   ├── formatter.py         # Size formatting, box drawing
│   ├── scanner.py           # Scanner class with os.scandir()
│   └── duplicate.py         # blake3 hashing, threaded dedup
├── ui/
│   ├── display.py           # Progress bars, result display
│   └── menu.py              # Interactive menu
├── exporters/
│   ├── csv_export.py        # CSV export
│   └── json_export.py       # JSON export
└── tests/
    └── test_formatter.py    # Unit tests
```

## Running tests

```bash
python -m pytest tests/ -v
```

## How duplicate detection works

1. **Walk** - Single `os.scandir()` pass groups files by size
2. **Header hash** - For each size group with 2+ files, hash only the first 4KB with blake3
3. **Full hash** - Only files with matching headers get fully hashed
4. **Threaded** - Separate size groups are hashed in parallel using `ThreadPoolExecutor`

This avoids reading entire files unless they're actual duplicates.

## License

MIT
