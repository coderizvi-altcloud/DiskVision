WIDTH = 65
DEFAULT_TOP_N = 20
SCAN_INTERVAL = 0.15
MAX_PATH_DISPLAY = 48
MAX_FOLDER_RESULTS = 20
HASH_WORKERS = 4
HASH_HEADER_SIZE = 4096
HASH_CHUNK_SIZE = 65536
BOX_EMPTY_ROWS = 22
PROGRESS_BAR_LEN = 30
HASH_PROGRESS_BAR_LEN = 20
HASH_PROGRESS_INTERVAL = 10

FILE_TYPES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff", ".raw"},
    "Videos": {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".m4v"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a"},
    "Documents": {".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".txt", ".csv", ".odt"},
    "Code": {".py", ".js", ".ts", ".java", ".c", ".cpp", ".h", ".cs", ".rb", ".go", ".rs", ".php", ".html", ".css", ".json", ".xml", ".yaml", ".yml"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz"},
    "Executables": {".exe", ".msi", ".bat", ".cmd", ".sh", ".ps1", ".app"},
}

SIZE_UNITS = [("GB", 1024**3), ("MB", 1024**2), ("KB", 1024)]
