import os
import tempfile
import pytest
from core.formatter import format_size, get_file_category
from core.models import FileEntry
from core.duplicate import hash_file_header, hash_file_full, hash_group
from exporters.csv_export import build_report_data


class TestFormatSize:
    def test_bytes(self):
        assert format_size(0) == "0 B"
        assert format_size(512) == "512 B"

    def test_kilobytes(self):
        assert format_size(1024) == "1.00 KB"
        assert format_size(1536) == "1.50 KB"

    def test_megabytes(self):
        assert format_size(1024**2) == "1.00 MB"
        assert format_size(5 * 1024**2) == "5.00 MB"

    def test_gigabytes(self):
        assert format_size(1024**3) == "1.00 GB"
        assert format_size(2.5 * 1024**3) == "2.50 GB"

    def test_terabytes_returns_gb(self):
        assert format_size(1024**4) == "1024.00 GB"


class TestGetFileCategory:
    def test_images(self):
        for ext in [".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp"]:
            assert get_file_category(ext) == "Images"

    def test_videos(self):
        for ext in [".mp4", ".mkv", ".avi", ".mov"]:
            assert get_file_category(ext) == "Videos"

    def test_audio(self):
        for ext in [".mp3", ".wav", ".flac"]:
            assert get_file_category(ext) == "Audio"

    def test_documents(self):
        for ext in [".pdf", ".doc", ".docx", ".txt"]:
            assert get_file_category(ext) == "Documents"

    def test_code(self):
        for ext in [".py", ".js", ".ts", ".java", ".c", ".cpp"]:
            assert get_file_category(ext) == "Code"

    def test_archives(self):
        for ext in [".zip", ".rar", ".7z", ".tar"]:
            assert get_file_category(ext) == "Archives"

    def test_executables(self):
        for ext in [".exe", ".msi", ".bat"]:
            assert get_file_category(ext) == "Executables"

    def test_other(self):
        assert get_file_category(".xyz") == "Other"
        assert get_file_category(".dat") == "Other"

    def test_case_insensitive(self):
        assert get_file_category(".JPG") == "Images"
        assert get_file_category(".Mp4") == "Videos"


class TestFileEntry:
    def test_ordering(self):
        a = FileEntry(100, "/a.txt")
        b = FileEntry(200, "/b.txt")
        assert a < b
        assert not b < a

    def test_equal_size(self):
        a = FileEntry(100, "/a.txt")
        b = FileEntry(100, "/b.txt")
        assert not a < b
        assert not b < a


class TestHashFile:
    def test_hash_file_header(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"hello world test data for header")
            path = f.name
        try:
            h1 = hash_file_header(path)
            h2 = hash_file_header(path)
            assert h1 is not None
            assert h1 == h2
        finally:
            os.unlink(path)

    def test_hash_file_full(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"full content for hashing test")
            path = f.name
        try:
            h1 = hash_file_full(path)
            h2 = hash_file_full(path)
            assert h1 is not None
            assert h1 == h2
        finally:
            os.unlink(path)

    def test_different_files_different_hashes(self):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"content A")
            path_a = f.name
        with tempfile.NamedTemporaryFile(delete=False, suffix=".bin") as f:
            f.write(b"content B")
            path_b = f.name
        try:
            assert hash_file_full(path_a) != hash_file_full(path_b)
        finally:
            os.unlink(path_a)
            os.unlink(path_b)

    def test_nonexistent_file(self):
        assert hash_file_header("/nonexistent/file.txt") is None
        assert hash_file_full("/nonexistent/file.txt") is None


class TestHashGroup:
    def test_finds_duplicates(self):
        content = b"identical content for duplicate test"
        files = []
        paths = []
        for _ in range(3):
            f = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
            f.write(content)
            f.close()
            files.append(f)
            paths.append(f.name)
        try:
            interrupted = lambda: False
            result = hash_group(paths, interrupted)
            assert len(result) == 2
            assert all(isinstance(d, tuple) and len(d) == 2 for d in result)
        finally:
            for p in paths:
                os.unlink(p)

    def test_no_duplicates_unique_files(self):
        paths = []
        for i in range(3):
            f = tempfile.NamedTemporaryFile(delete=False, suffix=".bin")
            f.write(f"unique content {i}".encode())
            f.close()
            paths.append(f.name)
        try:
            interrupted = lambda: False
            result = hash_group(paths, interrupted)
            assert len(result) == 0
        finally:
            for p in paths:
                os.unlink(p)


class TestBuildReportData:
    def test_basic_report(self):
        from core.models import FileEntry

        top_files = [FileEntry(1000, "/a.txt"), FileEntry(500, "/b.txt")]
        type_stats = {"Documents": {"count": 2, "bytes": 1500}}
        folder_sizes = {"/": 1500}
        duplicates = []
        data = build_report_data(top_files, type_stats, folder_sizes, duplicates, "/", 2, 1500)

        assert data["directory"] == "/"
        assert data["total_files"] == 2
        assert data["total_size_bytes"] == 1500
        assert len(data["largest_files"]) == 2
        assert data["largest_files"][0]["rank"] == 1
        assert data["largest_files"][0]["size_bytes"] == 1000

    def test_report_with_duplicates(self):
        from core.models import FileEntry

        top_files = [FileEntry(100, "/a.txt")]
        type_stats = {}
        folder_sizes = {}
        duplicates = [("/dup.txt", "/original.txt", 100)]
        data = build_report_data(top_files, type_stats, folder_sizes, duplicates, "/", 1, 100)

        assert len(data["duplicates"]) == 1
        assert data["duplicates"][0]["path"] == "/dup.txt"
        assert data["duplicates"][0]["original"] == "/original.txt"
