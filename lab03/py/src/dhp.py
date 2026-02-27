import tkinter as tk

from drivers import BaseDownloadingProgressHandler


class DPH(BaseDownloadingProgressHandler):
    """
    Download processor.
    Visualizes the process of downloading a book in the console.
    """

    def __init__(self, label: tk.Label):
        super().__init__()
        self._label = label

    def show_progress(self):
        self._label.config(
            text=f"\r{self.status.value}: {self._done_count}/{self._total_count}\t"
            f"{round(self._done_count / (self._total_count / 100), 2)} %"
        )
