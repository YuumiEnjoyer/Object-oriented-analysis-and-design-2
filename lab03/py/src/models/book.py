import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

type BookFiles = dict[str, str]


@dataclass
class Chapter:
    title: str
    url: str
    file_index: int
    start_time: int
    end_time: int

    @property
    def duration(self) -> int:
        return self.end_time - self.start_time


@dataclass(kw_only=True)
class BookSource(ABC):
    url: str = ""
    cover: str = ""

    @property
    @abstractmethod
    def dir_path(self) -> Path:
        pass

    @property
    def cover_path(self) -> Path:
        return Path("cover.jpg")


@dataclass(kw_only=True)
class TextBook(BookSource):
    publication: str
    file_url: str

    @property
    def dir_path(self) -> Path:
        return Path(".")


@dataclass(kw_only=True)
class AudioBook(BookSource):
    narrator: str
    chapters: list[Chapter]

    @property
    def dir_path(self) -> Path:
        return Path(".", self.narrator)


@dataclass(kw_only=True)
class BookData:
    title: str
    author: str
    series_name: str
    number_in_series: str

    @property
    def book_path(self) -> Path:
        """
        :returns: Relative path to the book in the library
        """
        path = Path(".", self.author)
        if self.series_name:
            book_name = (
                f"{str(self.number_in_series).rjust(2, '0')}. {self.title}"
            )
            path /= self.series_name
            path /= book_name
        else:
            path /= self.title
        return path

    @property
    def dir_path(self) -> Path:
        """
        :returns: Absolute path to the directory where the book is stored
        """
        return Path(os.environ["books_folder"], self.book_path).absolute()

    @property
    def cover_path(self) -> Path:
        """
        :returns: Absolute path to the book cover file
        """
        return self.dir_path / "cover.jpg"


@dataclass(kw_only=True)
class RawBook[SourceT: BookSource](BookData):
    source: SourceT

    @property
    def dir_path(self) -> Path:
        return super().dir_path / self.source.dir_path

    def __format__(self, format_spec: str, /) -> str:
        return repr(self)
