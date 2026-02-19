from db import DB, IDB
from models import RawBook


class DBProxy:
    def __init__(self, db_path: str):
        self._db_path = db_path
        self.__db: IDB | None = None
        self._cache: dict[int, RawBook] = {}

    @property
    def _db(self) -> IDB:
        if self.__db is None:
            self.__db = DB(self._db_path)
        return self.__db

    def insert_book(self, book: RawBook) -> RawBook:
        book = self._db.insert_book(book)
        self._cache[book.id] = book
        return book

    def get_book_by_id(self, book_id: int) -> RawBook | None:
        if book_id in self._cache:
            return self._cache[book_id]
        book = self._db.get_book_by_id(book_id)
        if book:
            self._cache[book_id] = book
        return book

    def get_all_books(self) -> list[RawBook]:
        return self._db.get_all_books()

    def update_download_status(self, book_id: int, downloaded: bool) -> None:
        self._db.update_download_status(book_id, downloaded)
        if book_id in self._cache and (book := self._cache.get(book_id)):
            book.downloaded = downloaded
