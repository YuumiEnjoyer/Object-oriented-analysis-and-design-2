import typing as ty

import psycopg2
from models import User

from ..base import DB


class RemoteDB(DB):
    def __init__(self):
        super().__init__()
        self._conn = psycopg2.connect(self._db_path)
        self._create_tables()

    def _create_tables(self):
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY NOT NULL,
                    username TEXT NOT NULL UNIQUE
                );
                """
            )
            self._conn.commit()

    def get_all_users(self) -> list[User]:
        with self._conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users;")
            data = cursor.fetchall()
        return [User(id=row[0], username=row[1]) for row in data]

    def register_user(self, user: User) -> User:
        with self._conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username) VALUES (%s) RETURNING id;
                """,
                (user.username,),
            )
            row = cursor.fetchone()
            self._conn.commit()
        user.id = ty.cast(tuple, row)[0]
        return user
