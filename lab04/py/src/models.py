from dataclasses import dataclass


@dataclass(kw_only=True)
class User:
    id: int = -1
    username: str
