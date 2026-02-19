import requests
from bs4 import BeautifulSoup
from models import RawBook


def find_book(url: str) -> RawBook:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")

    title = soup.select_one(".main-info__title").text.strip()
    author = soup.select_one("a.main-info__link[href^='/avtor']").text.strip()
    file_url = (
        "https://readli.net"
        + soup.select_one(".download__item:not(.disabled) a").attrs["href"]
    )

    return RawBook(
        title=title,
        author=author,
        file_url=file_url,
    )
