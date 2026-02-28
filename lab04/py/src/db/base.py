from __future__ import annotations

import importlib
import os
from abc import ABC, abstractmethod

from models import User


class DB(ABC):
    _instance: DB | None = None

    def __init__(self):
        self._db_path = os.environ.get("DB_PATH", "")
        if not self._db_path:
            raise ValueError("DB_PATH environment variable not set")

    @classmethod
    def get_instance(cls) -> DB:
        if not cls._instance:
            cls._instance = cls._get_plugin()
        return cls._instance

    @classmethod
    def _get_plugin(cls) -> DB:
        if not (plugin_name := os.environ.get("DB_TYPE")):
            raise ValueError("DB_TYPE environment variable not set")
        try:
            module = importlib.import_module(
                f".{plugin_name}", package=f"{__package__}.dbs"
            )
            plugin_impl = getattr(module, f"{plugin_name.capitalize()}DB")
        except (ModuleNotFoundError, AttributeError) as err:
            raise ValueError(
                f"`{plugin_name}` DB plugin not implemented"
            ) from err

        return plugin_impl()

    @abstractmethod
    def get_all_users(self) -> list[User]:
        """Returns all users from the database"""

    @abstractmethod
    def register_user(self, user: User) -> User:
        """Registers a new user in the database"""
