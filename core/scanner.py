import os
import sys
import time
import heapq
from collections import defaultdict
from colorama import Fore
from core.constants import DEFAULT_TOP_N, SCAN_INTERVAL
from core.models import FileEntry
from core.logger import get_logger
from core.formatter import format_size, get_file_category
from core.duplicate import hash_duplicates
from ui.display import display_progress, display_hash_progress

logger = get_logger(__name__)


class Scanner:
    def __init__(self):
        self.interrupted = False
        self.skipped_files = set()

    def interrupt(self):
        self.interrupted = True

    def _is_interrupted(self):
        return self.interrupted

    def scandir_recursive(self, target_path, callback):
        stack = [target_path]
        while stack:
            if self.interrupted:
                break
            current = stack.pop()
            try:
                with os.scandir(current) as it:
                    for entry in it:
                        if self.interrupted:
                            break
                        try:
                            is_dir = entry.is_dir(follow_symlinks=False)
                        except OSError:
                            continue
                        if is_dir:
                            stack.append(entry.path)
                        else:
                            try:
                                st = entry.stat(follow_symlinks=False)
                                callback(entry.path, st)
                            except (PermissionError, OSError) as e:
                                self.skipped_files.add(entry.path)
                                logger.warning("Skipped %s: %s", entry.path, e)
            except PermissionError as e:
                self.skipped_files.add(current)
                logger.warning("Permission denied: %s", e)
            except OSError as e:
                logger.warning("OS error: %s", e)

    def scan_files(self, target_path, extensions=None, min_size=0, max_size=None,
                   search_name=None, top_n=DEFAULT_TOP_N, no_hash=False):
        self.interrupted = False
        self.skipped_files = set()

        if not os.path.isdir(target_path):
            return None, 0, 0, {}, {}, []

        top_files = []
        file_count = 0
        total_bytes = 0
        type_stats = defaultdict(lambda: {"count": 0, "bytes": 0})
        folder_sizes = defaultdict(int)
        size_groups = defaultdict(list)

        start_time = time.time()
        last_display = time.time()
        root = os.path.normcase(os.path.normpath(target_path))

        def on_file(path_str, st):
            nonlocal file_count, total_bytes, last_display
            size = st.st_size

            now = time.time()
            if now - last_display >= SCAN_INTERVAL:
                display_progress(file_count, total_bytes, now - start_time)
                last_display = now

            if size < min_size:
                return
            if max_size is not None and size > max_size:
                return

            ext = os.path.splitext(path_str)[1].lower()
            if extensions and ext not in extensions:
                return
            if search_name and search_name.lower() not in os.path.basename(path_str).lower():
                return

            file_count += 1
            total_bytes += size

            category = get_file_category(ext)
            type_stats[category]["count"] += 1
            type_stats[category]["bytes"] += size

            parent = os.path.dirname(path_str)
            while True:
                folder_sizes[parent] += size
                if os.path.normcase(os.path.normpath(parent)) == root:
                    break
                new_parent = os.path.dirname(parent)
                if new_parent == parent:
                    break
                parent = new_parent

            size_groups[size].append(path_str)

            entry = FileEntry(size, path_str)
            if len(top_files) < top_n:
                heapq.heappush(top_files, entry)
            elif size > top_files[0].size:
                heapq.heapreplace(top_files, entry)

        self.scandir_recursive(target_path, on_file)

        elapsed = time.time() - start_time
        display_progress(file_count, total_bytes, elapsed)
        sys.stdout.write("\r" + " " * 90 + "\r")
        sys.stdout.flush()

        duplicates = []
        if not no_hash:
            print(f"  {Fore.CYAN}Hashing duplicates...{Style.RESET_ALL}")
            duplicates = hash_duplicates(size_groups, self._is_interrupted, display_hash_progress)

        top_files_sorted = sorted(top_files, key=lambda e: e.size, reverse=True)

        return top_files_sorted, file_count, total_bytes, dict(type_stats), dict(folder_sizes), duplicates
