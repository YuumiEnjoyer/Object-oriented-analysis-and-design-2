import os
import threading
import tkinter as tk
from tkinter import messagebox

from db_proxy import DBProxy
from downloader import download
from drivers import find_book
from models import RawBook

# Константы
DB_PATH = "../storage/books.db"
DOWNLOAD_PATH = "../storage/downloads/"


class BookApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Библиотека книг")
        self.root.geometry("600x500")

        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        self.db_proxy = DBProxy(DB_PATH)

        self.setup_ui()
        self.load_books_from_db()

    def setup_ui(self):
        # Верхняя панель для добавления книг
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10, padx=10, fill=tk.X)

        tk.Label(top_frame, text="URL книги:").pack(side=tk.LEFT)
        self.url_entry = tk.Entry(top_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=(5, 5))

        self.add_button = tk.Button(
            top_frame,
            text="Добавить в библиотеку",
            command=self.add_book_threaded,
        )
        self.add_button.pack(side=tk.LEFT, padx=(5, 0))

        # Рамка для списка книг с прокруткой
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

        # Создаем Canvas и Scrollbar
        self.canvas = tk.Canvas(list_frame)
        scrollbar = tk.Scrollbar(
            list_frame, orient="vertical", command=self.canvas.yview
        )
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )

        self.canvas.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Словарь для хранения кнопок скачивания
        self.download_buttons = {}

    def add_book_threaded(self):
        """Запуск добавления книги в отдельном потоке"""
        thread = threading.Thread(target=self.add_book)
        thread.daemon = True
        thread.start()

    def add_book(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Ошибка", "Введите URL книги")
            return

        try:
            # Блокируем кнопку во время выполнения
            self.add_button.config(state=tk.DISABLED)

            book = find_book(url)
            book.downloaded = False  # По умолчанию книга не скачана
            book = self.db_proxy.insert_book(book)

            # Добавляем книгу в UI
            self.add_book_to_ui(book)
            self.url_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось добавить книгу: {str(e)}"
            )
        finally:
            self.root.after(0, lambda: self.add_button.config(state=tk.NORMAL))

    def load_books_from_db(self):
        """Загрузка всех книг из базы данных при запуске"""
        try:
            books = self.db_proxy.get_all_books()
            for book in books:
                self.add_book_to_ui(book)
        except Exception as e:
            messagebox.showerror(
                "Ошибка", f"Не удалось загрузить книги: {str(e)}"
            )

    def add_book_to_ui(self, book: RawBook):
        """Добавление книги в интерфейс"""
        book_frame = tk.Frame(
            self.scrollable_frame, relief=tk.RAISED, borderwidth=1
        )
        book_frame.pack(fill=tk.X, pady=2, padx=5)

        # Текстовая метка с информацией о книге
        book_label = tk.Label(
            book_frame, text=f"{book.author} - {book.title}", anchor="w"
        )
        book_label.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))

        # Кнопка скачивания
        download_button = tk.Button(
            book_frame,
            text="Скачать",
            command=lambda: self.download_book_threaded(book, download_button),
        )
        download_button.pack(side=tk.RIGHT, padx=5)

        # Если книга уже скачана, делаем кнопку неактивной
        if book.downloaded:
            download_button.config(text="Скачано", state=tk.DISABLED)

        # Сохраняем ссылку на кнопку для будущих обновлений
        self.download_buttons[book.id] = download_button

    def download_book_threaded(self, book: RawBook, button):
        """Запуск скачивания книги в отдельном потоке"""
        thread = threading.Thread(
            target=self.download_book, args=(book, button)
        )
        thread.daemon = True
        thread.start()

    def download_book(self, book: RawBook, button):
        """Скачивание книги"""
        try:
            # Блокируем кнопку во время скачивания
            button.config(state=tk.DISABLED, text="Скачивание...")

            # Получаем актуальную информацию о книге из БД
            fresh_book = self.db_proxy.get_book_by_id(book.id)
            if fresh_book and fresh_book.downloaded:
                button.config(text="Скачано", state=tk.DISABLED)
                return

            full_path = os.path.join(DOWNLOAD_PATH, book.get_path())
            if download(book, full_path):
                # Обновляем статус в БД
                self.db_proxy.update_download_status(book.id, True)

                # Обновляем кнопку в UI
                button.config(text="Скачано", state=tk.DISABLED)
                messagebox.showinfo(
                    "Успех", f"Книга '{book.title}' успешно скачана!"
                )
            else:
                button.config(state=tk.NORMAL, text="Скачать")
                messagebox.showerror("Ошибка", "Не удалось скачать книгу")

        except Exception as e:
            button.config(state=tk.NORMAL, text="Скачать")
            messagebox.showerror("Ошибка", f"Ошибка при скачивании: {str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()
