import sqlite3

from models import User

from ..base import DB


class LocalDB(DB):
    def __init__(self):
        super().__init__()
        self._conn = sqlite3.connect(
            self._db_path, check_same_thread=False, isolation_level=None
        )
        self._create_tables()

    def _create_tables(self):
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE
            );
            """
        )

    def get_all_users(self) -> list[User]:
        data = self._conn.execute("SELECT * FROM users;").fetchall()
        return [User(id=row[0], username=row[1]) for row in data]

    def register_user(self, user: User) -> User:
        row = self._conn.execute(
            """
            INSERT INTO users (username) VALUES (?) RETURNING id;
            """,
            (user.username,),
        ).fetchone()
        user.id = row[0]
        return user
