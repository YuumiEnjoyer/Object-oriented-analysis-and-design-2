import os

import requests
from models import RawBook


def download(book: RawBook, destination_path: str) -> bool:
    try:
        # Создаем директорию если она не существует
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        data = requests.get(book.file_url)
        with open(destination_path, "wb") as file:
            file.write(data.content)
        return True
    except Exception:
        return False
