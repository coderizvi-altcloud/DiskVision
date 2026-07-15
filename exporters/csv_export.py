import csv
from datetime import datetime
from core.constants import MAX_FOLDER_RESULTS
from core.formatter import format_size


def build_report_data(top_files, type_stats, folder_sizes, duplicates, target_path, count, total_bytes):
    return {
        "directory": target_path,
        "total_files": count,
        "total_size_bytes": total_bytes,
        "total_size_formatted": format_size(total_bytes),
        "scan_time": datetime.now().isoformat(),
        "largest_files": [{"rank": i, "size_bytes": e.size, "size": format_size(e.size), "path": e.path} for i, e in enumerate(top_files, 1)],
        "file_types": {cat: {"count": info["count"], "bytes": info["bytes"], "size": format_size(info["bytes"])} for cat, info in type_stats.items()},
        "largest_folders": [{"size_bytes": s, "size": format_size(s), "path": p} for p, s in sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True)[:MAX_FOLDER_RESULTS]],
        "duplicates": [{"size_bytes": s, "size": format_size(s), "path": d, "original": o} for d, o, s in duplicates],
    }


def export_csv(top_files, type_stats, folder_sizes, duplicates, target_path, count, total_bytes):
    filename = f"disk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    data = build_report_data(top_files, type_stats, folder_sizes, duplicates, target_path, count, total_bytes)
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["=== DISK INFOGETTER REPORT ==="])
        writer.writerow(["Directory", data["directory"]])
        writer.writerow(["Total Files", data["total_files"]])
        writer.writerow(["Total Size", data["total_size_formatted"]])
        writer.writerow([])
        writer.writerow(["=== LARGEST FILES ==="])
        writer.writerow(["Rank", "Size (Bytes)", "Size", "Path"])
        for entry in data["largest_files"]:
            writer.writerow([entry["rank"], entry["size_bytes"], entry["size"], entry["path"]])
        writer.writerow([])
        writer.writerow(["=== FILE TYPE STATS ==="])
        writer.writerow(["Type", "Count", "Size (Bytes)", "Size"])
        for cat, info in sorted(data["file_types"].items(), key=lambda x: x[1]["bytes"], reverse=True):
            writer.writerow([cat, info["count"], info["bytes"], info["size"]])
        writer.writerow([])
        writer.writerow(["=== LARGEST FOLDERS ==="])
        writer.writerow(["Size (Bytes)", "Size", "Path"])
        for folder in data["largest_folders"]:
            writer.writerow([folder["size_bytes"], folder["size"], folder["path"]])
        if data["duplicates"]:
            writer.writerow([])
            writer.writerow(["=== DUPLICATES ==="])
            writer.writerow(["Size (Bytes)", "Size", "Path", "Duplicate Of"])
            for dup in data["duplicates"]:
                writer.writerow([dup["size_bytes"], dup["size"], dup["path"], dup["original"]])
    print(f"  Exported to {filename}")
