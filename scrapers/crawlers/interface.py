from ..driver import FireFoxDriver
from abc import ABC, abstractmethod


class PageCrawler(ABC):
    def __init__(self):
        self.__driver = FireFoxDriver()

    @abstractmethod
    def get_id(url: str) -> str:
        pass

    @abstractmethod
    def get_directors(element) -> list[str]:
        pass

    @abstractmethod
    def get_cast(element) -> list[str]:
        pass

    @abstractmethod
    def get_plot(element) -> str:
        pass

    @abstractmethod
    def get_run_time(element) -> str:
        pass

    @abstractmethod
    def get_genres(element) -> list[str]:
        pass

    @abstractmethod
    def get_release_date(element) -> str:
        pass

    @abstractmethod
    def get_origins(element) -> list[str]:
        pass

    @abstractmethod
    def get_languages(element) -> list[str]:
        pass

    @abstractmethod
    def get_entry(self, url, name="") -> dict:
        pass

    def restart(self):
        """Get a new driver"""
        self.terminate()
        self.__driver = FireFoxDriver()

    def terminate(self):
        """Terminate the crawler."""
        self.__driver.quit()
