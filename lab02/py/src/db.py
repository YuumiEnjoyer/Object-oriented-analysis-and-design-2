import sqlite3
import typing as ty

from models import RawBook


class IDB(ty.Protocol):
    def __init__(self, db_path: str): ...
    def insert_book(self, book: RawBook) -> RawBook: ...
    def get_book_by_id(self, book_id: int) -> RawBook | None: ...
    def get_all_books(self) -> list[RawBook]: ...
    def update_download_status(
        self, book_id: int, downloaded: bool
    ) -> None: ...


class DB:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self._db = sqlite3.connect(
            self._db_path, isolation_level=None, check_same_thread=False
        )
        self._create_tables()

    def _create_tables(self):
        self._db.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                file_url TEXT NOT NULL,
                downloaded BOOLEAN NOT NULL DEFAULT FALSE
            )
        """)

    def insert_book(self, book: RawBook) -> RawBook:
        bid = self._db.execute(
            """
            INSERT INTO books (title, author, file_url, downloaded)
            VALUES (?, ?, ?, ?) RETURNING id
            """,
            (book.title, book.author, book.file_url, book.downloaded),
        ).fetchone()[0]
        book.id = bid
        return book

    def get_book_by_id(self, book_id: int) -> RawBook | None:
        cursor = self._db.execute(
            """
            SELECT id, title, author, file_url, downloaded
            FROM books
            WHERE id = ?
            """,
            (book_id,),
        )
        if row := cursor.fetchone():
            return RawBook(
                id=row[0],
                title=row[1],
                author=row[2],
                file_url=row[3],
                downloaded=bool(row[4]),
            )
        return None

    def get_all_books(self) -> list[RawBook]:
        cursor = self._db.execute("""
            SELECT id, title, author, file_url, downloaded
            FROM books
        """)
        return [
            RawBook(
                id=row[0],
                title=row[1],
                author=row[2],
                file_url=row[3],
                downloaded=bool(row[4]),
            )
            for row in cursor.fetchall()
        ]

    def update_download_status(self, book_id: int, downloaded: bool) -> None:
        self._db.execute(
            """
            UPDATE books
            SET downloaded = ?
            WHERE id = ?
            """,
            (downloaded, book_id),
        )
