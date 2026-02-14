import asyncio
import os

from drivers import BaseDriver
from drivers.downloaders import MP3Downloader, ZipDownloader
from drivers.drivers import KnigaVUhe, Readli
from stdout_dhp import StdoutDPH

os.environ["BOOKS_FOLDER"] = "../downloads"
if not os.path.exists(os.environ["BOOKS_FOLDER"]):
    os.makedirs(os.environ["BOOKS_FOLDER"])


def main():
    url = input("Enter a URL: ")

    driver = BaseDriver.get_suitable_driver(url)()
    book = driver.get_book(url)

    dhp = StdoutDPH()
    if isinstance(driver, KnigaVUhe):
        downloader = MP3Downloader(book, dhp)
    elif isinstance(driver, Readli):
        downloader = ZipDownloader(book, dhp)
    else:
        raise ValueError("Unsupported driver")

    asyncio.run(downloader.download_book())


if __name__ == "__main__":
    main()
