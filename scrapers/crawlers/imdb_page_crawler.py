from .interface import PageCrawler
from ..drivers import FireFoxDriver
from ..utility.data import get_field_names
from ..utility.wrapper import data_fallback

from datetime import datetime
from selenium.webdriver.common.by import By


class ImdbPageCrawler(PageCrawler):
    FIELD_NAMES = get_field_names("imdb")

    def __init__(self):
        self.__driver = FireFoxDriver()

    def restart(self):
        self.terminate()
        self.__driver = FireFoxDriver()

    def terminate(self) -> None:
        self.__driver.close()

    @data_fallback(None)
    def _get_rating(element) -> str:
        rating = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating']"
        ).text.split("\n")[1]
        return rating

    @data_fallback(None)
    def _get_vote_count(element) -> str:
        rating = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating']"
        ).text.split("\n")[-1]
        return rating

    @data_fallback([])
    def _get_directors(element) -> list[str]:
        cast_field = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt']",
        )
        director_field = cast_field.find_elements(
            By.CSS_SELECTOR,
            "div[class='ipc-metadata-list-item__content-container']",
        )[0]
        directors = director_field.find_elements(
            By.CSS_SELECTOR,
            "a[class='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link']",
        )
        return [d.text for d in directors]

    @data_fallback([])
    def _get_cast(element) -> list[str]:
        # return element.text
        casts = element.find_elements(
            By.CSS_SELECTOR, "a[class='sc-cd7dc4b7-1 kVdWAO']"
        )
        return [c.text for c in casts]

    @data_fallback(None)
    def _get_plot(element) -> str:
        return element.find_element(By.CSS_SELECTOR, "span[data-testid='plot-xl']").text

    @data_fallback(None)
    def _get_run_time(element) -> str:
        runtime = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']",
        ).text.split("\n")[-1]
        formats = ["%Hh %Mm", "%Hh", "%Mm"]
        for format in formats:
            try:
                runtime = datetime.strptime(runtime, format)
                return runtime.strftime("%H:%M:%S")
            except ValueError:
                continue

    @data_fallback([])
    def _get_genres(element) -> list[str]:
        fields = element.find_elements(
            By.CSS_SELECTOR, "a[class='ipc-chip ipc-chip--on-baseAlt']"
        )
        genres = [f.text for f in fields]
        return genres

    @data_fallback(None)
    def _get_release_date(element) -> str:
        formats = ["%B %d, %Y", "%B %Y", "%Y"]
        rformats = ["%Y-%m-%d", "%Y-%m", "%Y"]
        date = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-releasedate']"
        ).text.split("\n")[-1]
        date = date[: date.rindex(" (")]
        for format, rformat in zip(formats, rformats):
            try:
                date = datetime.strptime(date, format)
                return date.strftime(rformat)
            except ValueError:
                continue

    @data_fallback(None)
    def _get_rdate_fallback(element) -> str:
        items: list[str] = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']",
        ).text.split("\n")
        for item in items:
            if item.isdecimal():
                return item

    @data_fallback([])
    def _get_origins(element) -> list[str]:
        origin_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-origin']"
        )
        origins = origin_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        origins = [o.text for o in origins]
        return origins

    @data_fallback([])
    def _get_languages(element) -> list[str]:
        language_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-languages']"
        )
        languages = language_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        languages = [lang.text for lang in languages]
        return languages

    def get_entry(self, imdb_id: int) -> dict:
        entry_dict = {"ImdbID": imdb_id}
        self.__driver.get(f"https://www.imdb.com/title/tt{imdb_id:07d}")
        elements = self.__driver.find_elements(By.TAG_NAME, "section")
        rdate_fallback = None
        for e in elements:
            if attr := e.get_attribute("data-testid"):
                match attr:
                    case "atf-wrapper-bg":
                        entry_dict["Plot"] = ImdbPageCrawler._get_plot(e)
                        entry_dict["Rating"] = ImdbPageCrawler._get_rating(e)
                        entry_dict["VoteCount"] = ImdbPageCrawler._get_vote_count(e)
                        entry_dict["Genres"] = ImdbPageCrawler._get_genres(e)
                        entry_dict["Runtime"] = ImdbPageCrawler._get_run_time(e)
                        entry_dict["Directors"] = ImdbPageCrawler._get_directors(e)
                        rdate_fallback = ImdbPageCrawler._get_rdate_fallback(e)
                    case "title-cast":
                        entry_dict["Cast"] = ImdbPageCrawler._get_cast(e)
                    case "Details":
                        entry_dict["ReleaseDate"] = (
                            ImdbPageCrawler._get_release_date(e) or rdate_fallback
                        )
                        entry_dict["OriginCountries"] = ImdbPageCrawler._get_origins(e)
                        entry_dict["Languages"] = ImdbPageCrawler._get_languages(e)
        return entry_dict
