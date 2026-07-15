import sys
from blake3 import blake3
from core.constants import HASH_HEADER_SIZE, HASH_CHUNK_SIZE
from core.logger import get_logger

logger = get_logger(__name__)


def hash_file_header(path_str):
    try:
        with open(path_str, "rb") as f:
            return blake3(f.read(HASH_HEADER_SIZE)).hexdigest()
    except (PermissionError, OSError, ValueError) as e:
        logger.warning("Header hash failed %s: %s", path_str, e)
        return None


def hash_file_full(path_str):
    try:
        h = blake3()
        with open(path_str, "rb") as f:
            for chunk in iter(lambda: f.read(HASH_CHUNK_SIZE), b""):
                h.update(chunk)
        return h.hexdigest()
    except (PermissionError, OSError, ValueError) as e:
        logger.warning("Full hash failed %s: %s", path_str, e)
        return None


def hash_group(paths, interrupted):
    header_hashes = {}
    for path_str in paths:
        if interrupted():
            return []
        hh = hash_file_header(path_str)
        if hh is not None:
            header_hashes.setdefault(hh, []).append(path_str)

    full_hashes = {}
    duplicates = []
    for hh, group in header_hashes.items():
        if interrupted():
            break
        if len(group) < 2:
            continue
        for path_str in group:
            if interrupted():
                break
            fh = hash_file_full(path_str)
            if fh is None:
                continue
            if fh in full_hashes:
                duplicates.append((path_str, full_hashes[fh]))
            else:
                full_hashes[fh] = path_str
    return duplicates


def hash_duplicates(size_groups, interrupted, progress_callback=None):
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from core.constants import HASH_WORKERS

    eligible = [(size, paths) for size, paths in size_groups.items() if len(paths) >= 2]
    total_groups = len(eligible)
    duplicates = []
    groups_done = 0

    with ThreadPoolExecutor(max_workers=HASH_WORKERS) as executor:
        futures = {}
        for size, paths in eligible:
            if interrupted():
                break
            futures[executor.submit(hash_group, paths, interrupted)] = size

        for future in as_completed(futures):
            if interrupted():
                break
            size = futures[future]
            groups_done += 1
            if progress_callback:
                progress_callback(groups_done, total_groups)
            try:
                for dup_path, original in future.result():
                    duplicates.append((dup_path, original, size))
            except Exception as e:
                logger.exception("Hash group failed: %s", e)

    sys.stdout.write("\r" + " " * 90 + "\r")
    sys.stdout.flush()
    return duplicates
