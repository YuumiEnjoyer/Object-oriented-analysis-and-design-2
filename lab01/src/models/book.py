from __future__ import annotations

import os
import typing as ty
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

type BookFiles = dict[str, str]


class BookStatus(Enum):
    NEW = "new"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


@dataclass
class ListeningProgress:
    chapter_index: int = 0
    time: int = 0


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
    id: int = -1
    url: str = ""
    cover: str = ""

    status: BookStatus = BookStatus.NEW
    files: BookFiles = field(default_factory=dict)
    """ Dict like {file_name: hash} """

    @property
    @abstractmethod
    def progress_percent(self) -> int:
        pass

    @property
    @abstractmethod
    def dir_path(self) -> Path:
        pass

    @property
    def cover_path(self) -> Path:
        return Path("cover.jpg")

    @property
    def is_downloaded(self) -> bool:
        return bool(self.files)

    def __repr__(self):
        return f"{self.__class__.__name__}(url={self.url})"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return (
                f"<g>{self.__class__.__name__}</g><w>("
                f"<le>url</le>=<y>{self.url}</y>)</w>"
            )
        return repr(self)


@dataclass(kw_only=True)
class TextBook(BookSource):
    publication: str
    file_url: str
    total_pages: int
    read_pages: int = 0

    @property
    def progress_percent(self) -> int:
        return int(round(self.read_pages / self.total_pages * 100))

    @property
    def dir_path(self) -> Path:
        return Path(".")


@dataclass(kw_only=True)
class AudioBook(BookSource):
    narrator: str
    duration: str
    chapters: list[Chapter]
    progress: ListeningProgress = field(default_factory=ListeningProgress)

    @property
    def progress_percent(self) -> int:
        if self.status == BookStatus.COMPLETED:
            return 100
        total = sum([chapter.duration for chapter in self.chapters])
        if not total:
            return 0
        cur = (
            sum(
                [
                    item.duration
                    for i, item in enumerate(self.chapters)
                    if i < self.progress.chapter_index
                ]
            )
            + self.progress.time
        )
        return int(round(cur / total * 100))

    @property
    def dir_path(self) -> Path:
        return Path(".", self.narrator)


class SourceType(Enum):
    AudioBook = AudioBook
    TextBook = TextBook


@dataclass(kw_only=True)
class BookData:
    title: str
    author: str
    series_name: str
    number_in_series: str
    description: str

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
class BookPreview(BookData):
    urls: list[str]
    cover: str
    narrators: list[str]
    publications: list[str]
    durations: list[str]


@dataclass(kw_only=True)
class RawBook[SourceT: BookSource](BookData):
    source: SourceT

    @property
    def dir_path(self) -> Path:
        return super().dir_path / self.source.dir_path

    def to_preview(self) -> BookPreview:
        narrators, publications, durations = [], [], []
        if isinstance(self.source, AudioBook):
            if self.source.narrator:
                narrators.append(self.source.narrator)
            if self.source.duration:
                durations.append(self.source.duration)
        elif isinstance(self.source, TextBook):
            if self.source.publication:
                publications.append(self.source.publication)
            if self.source.total_pages:
                durations.append(self.source.total_pages)
        return BookPreview(
            title=self.title,
            author=self.author,
            series_name=self.series_name,
            number_in_series=self.number_in_series,
            description=self.description,
            urls=[self.source.url],
            cover=self.source.cover,
            narrators=narrators,
            publications=publications,
            durations=durations,
        )

    def __repr__(self):
        return f"RawBook(title={self.title}, source={self.source})"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return (
                f"<g>RawBook</g><w>("
                f"<le>title</le>=<y>{self.title}</y>, "
                f"<le>source</le>={self.source:colored})</w>"
            )
        return repr(self)


@dataclass(kw_only=True)
class Book(BookData):
    cover: str
    adding_date: datetime = field(default_factory=datetime.now)
    favorite: bool = False
    status: BookStatus = BookStatus.NEW

    _text_sources: list[TextBook] = field(default_factory=list)
    _audio_sources: list[AudioBook] = field(default_factory=list)

    def iter_sources(self) -> ty.Generator[BookSource]:
        yield from self._text_sources
        yield from self._audio_sources

    def add_text_source(self, source: TextBook) -> None:
        self._text_sources.append(source)

    def add_audio_source(self, source: AudioBook) -> None:
        self._audio_sources.append(source)

    def to_raw_book[T: BookSource](self, source: T) -> RawBook[T]:
        return RawBook(
            title=self.title,
            author=self.author,
            series_name=self.series_name,
            number_in_series=self.number_in_series,
            description=self.description,
            source=source,
        )

    def __repr__(self):
        return f"Book(title={self.title})"

    def __format__(self, format_spec):
        if format_spec == "colored":
            return f"<g>Book</g><w>(<le>title</le>=<y>{self.title}</y>)</w>"
        return repr(self)
