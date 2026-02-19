import os
from dataclasses import dataclass


@dataclass(kw_only=True)
class RawBook:
    id: int = -1
    title: str
    author: str
    file_url: str
    downloaded: bool = False

    def get_path(self):
        return os.path.join(self.author, self.title)
