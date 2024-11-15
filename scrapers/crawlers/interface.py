from abc import ABC, abstractmethod


class PageCrawler(ABC):
    FIELD_NAMES: list[str] = []

    @abstractmethod
    def get_entry(self, movie_id: int) -> dict:
        pass
