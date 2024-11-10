from ..drivers import FireFoxDriver
from abc import ABC, abstractmethod


class PageCrawler(ABC):
    FIELD_NAMES: list[str] = []

    def __init__(self):
        self._driver = FireFoxDriver()

    @abstractmethod
    def _get_id(url: str) -> str:
        pass

    @abstractmethod
    def _get_directors(element) -> list[str]:
        pass

    @abstractmethod
    def _get_cast(element) -> list[str]:
        pass

    @abstractmethod
    def _get_plot(element) -> str:
        pass

    @abstractmethod
    def _get_run_time(element) -> str:
        pass

    @abstractmethod
    def _get_genres(element) -> list[str]:
        pass

    @abstractmethod
    def _get_release_date(element) -> str:
        pass

    @abstractmethod
    def _get_origins(element) -> list[str]:
        pass

    @abstractmethod
    def _get_languages(element) -> list[str]:
        pass

    @abstractmethod
    def get_entry(self, url, name="") -> dict:
        pass

    def restart(self):
        """Get a new driver"""
        self.terminate()
        self._driver = FireFoxDriver()

    def terminate(self):
        """Terminate the crawler."""
        self._driver.quit()
