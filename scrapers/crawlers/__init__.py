from .interface import PageCrawler
from .imdb_page_crawler import ImdbPageCrawler

from typing import Literal


def get_crawler(website: Literal["imdb", "tmdb"]) -> PageCrawler:
    match website:
        case "imdb":
            return ImdbPageCrawler()
        case "moviedb":
            return None
