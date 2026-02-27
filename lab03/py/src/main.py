import asyncio
import os
import threading
import tkinter as tk
import typing as ty

from dhp import DPH
from drivers.base_downloader import BaseDownloader
from drivers.downloaders import M3U8Downloader, MP3Downloader, ZipDownloader
from models.book import AudioBook, Chapter, RawBook, TextBook

os.environ["books_folder"] = "../../downloads"

if not os.path.exists(os.environ["books_folder"]):
    os.makedirs(os.environ["books_folder"])

DATA: list[RawBook] = [
    RawBook(
        title="Мать ученья",
        author="Domagoj Kurmaic",
        series_name="",
        number_in_series="",
        source=TextBook(
            url="https://readli.net/mat-uchenya/",
            cover="https://readli.net/wp-content/uploads/2024/02/1275666.jpg",
            publication="Readli",
            file_url="https://readli.net/download.php?id=552504",
        ),
    ),
    RawBook(
        title="Мухи",
        author="Айзек Азимов",
        series_name="",
        number_in_series="",
        source=AudioBook(
            url="https://knigavuhe.org/book/29804-mukhi/",
            cover="https://s5.knigavuhe.org/1/covers/29804/1-2.jpg?v=1",
            narrator="Смолин Константин",
            chapters=[
                Chapter(
                    title="Мухи",
                    url="https://s12.knigavuhe.org/1/audio/29804/muhi-azimov.mp3",
                    file_index=0,
                    start_time=0,
                    end_time=1171,
                ),
            ],
        ),
    ),
]


def download_book(book: RawBook):
    if book.source.url.startswith("https://readli.net"):
        downloader = ZipDownloader
    elif book.source.url.startswith("https://knigavuhe.org"):
        downloader = MP3Downloader
    elif book.source.url.startswith("https://akniga.orh"):
        downloader = M3U8Downloader
    else:
        raise RuntimeError()

    t = threading.Thread(target=lambda: _download(downloader, book))
    t.start()


def _download(downloader: ty.Type[BaseDownloader], book: RawBook):
    if asyncio.run(downloader(book, DPH(progress_label)).download_book()):
        progress_label.config(text=f"Скачивание книги {book.title} завершено")
    else:
        progress_label.config(text=f"Ошибка скачивания книги {book.title}")


root = tk.Tk()
root.title("Book Downloader")
root.geometry("350x200")

for book in DATA:
    book_frame = tk.Frame(root, relief=tk.RAISED, borderwidth=1)
    book_frame.pack(fill=tk.X, pady=2, padx=5)

    book_label = tk.Label(
        book_frame, text=f"{book.title} - {book.author}", anchor="w"
    )
    book_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

    download_button = tk.Button(
        book_frame,
        text="Скачать",
        command=lambda book=book: download_book(book),
    )
    download_button.pack(side=tk.RIGHT, padx=5)


progress_label = tk.Label(root, text="")
progress_label.pack(side=tk.BOTTOM, fill=tk.X, padx=5)

root.mainloop()
