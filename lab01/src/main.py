import os
import threading
import tkinter
from tkinter import filedialog

from drivers import BaseDownloadingProgressHandler, BaseDriver

os.environ["BOOKS_FOLDER"] = "../downloads"
if not os.path.exists(os.environ["BOOKS_FOLDER"]):
    os.makedirs(os.environ["BOOKS_FOLDER"])


class TkinterDPH(BaseDownloadingProgressHandler):
    """
    Download processor.
    Visualizes the process of downloading a book in the console.
    """

    def show_progress(self):
        lb_status.config(
            text=f"\r{self.status.value}: {self._done_count}/{self._total_count}\t"
            f"{round(self._done_count / (self._total_count / 100), 2)} %"
        )


def select_folder():
    f = filedialog.askdirectory()
    if f:
        os.environ["BOOKS_FOLDER"] = f


def start_download():
    url = input.get()
    if not url:
        return
    btn.pack_forget()
    folder_btn.pack_forget()

    driver = BaseDriver.get_suitable_driver(url)()
    t = threading.Thread(target=lambda: driver.download_book(url, TkinterDPH()))
    t.start()


window = tkinter.Tk()
window.geometry("300x150")

lb = tkinter.Label(window, text="enter url")
lb.pack()
input = tkinter.Entry(window)
input.pack()
btn = tkinter.Button(window, text="download", command=start_download)
btn.pack()
folder_btn = tkinter.Button(window, text="select folder", command=select_folder)
folder_btn.pack()

lb_status = tkinter.Label(window, text="")
lb_status.pack()

window.mainloop()
