from dataclasses import dataclass


@dataclass
class FileEntry:
    size: int
    path: str

    def __lt__(self, other):
        return self.size < other.size
