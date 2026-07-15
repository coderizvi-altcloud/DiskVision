import json
from datetime import datetime
from exporters.csv_export import build_report_data


def export_json(top_files, type_stats, folder_sizes, duplicates, target_path, count, total_bytes):
    filename = f"disk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    data = build_report_data(top_files, type_stats, folder_sizes, duplicates, target_path, count, total_bytes)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"  Exported to {filename}")
