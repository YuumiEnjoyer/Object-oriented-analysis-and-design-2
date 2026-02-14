import os

from drivers import BaseDriver
from stdout_dhp import StdoutDPH

os.environ["BOOKS_FOLDER"] = "../downloads"
if not os.path.exists(os.environ["BOOKS_FOLDER"]):
    os.makedirs(os.environ["BOOKS_FOLDER"])


def main():
    url = input("Enter a URL: ")

    driver = BaseDriver.get_suitable_driver(url)()
    driver.download_book(url, StdoutDPH())


if __name__ == "__main__":
    main()
