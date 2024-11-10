from .interface import PageCrawler
from ..utility.wrapper import data_fallback

from selenium.webdriver.common.by import By
from datetime import datetime


class ImdbPageCrawler(PageCrawler):
    def get_id(url) -> str:
        return url.removeprefix("https://www.imdb.com/title/")[:-1]

    @data_fallback([])
    def get_directors(element) -> list[str]:
        cast_field = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt']",
        )
        director_field = cast_field.find_elements(
            By.CSS_SELECTOR,
            "li[class='ipc-metadata-list__item']",
        )[0]
        directors = director_field.find_elements(
            By.CSS_SELECTOR,
            "a[class='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link']",
        )
        return [d.text for d in directors]

    @data_fallback([])
    def get_cast(element) -> list[str]:
        # return element.text
        casts = element.find_elements(
            By.CSS_SELECTOR, "a[class='sc-cd7dc4b7-1 kVdWAO']"
        )
        return [c.text for c in casts]

    @data_fallback
    def get_plot(element) -> str:
        return element.find_element(By.CSS_SELECTOR, "span[data-testid='plot-xl']").text

    @data_fallback
    def get_run_time(element) -> str:
        runtime = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']",
        ).text.split("\n")[-1]
        runtime = datetime.strptime(runtime, "%Hh %Mm")
        return runtime.strftime("%H:%M:%S")

    @data_fallback([])
    def get_genres(element) -> list[str]:
        fields = element.find_elements(
            By.CSS_SELECTOR, "a[class='ipc-chip ipc-chip--on-baseAlt']"
        )
        genres = [f.text for f in fields]
        return genres

    @data_fallback
    def get_release_date(element) -> str:
        date = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-releasedate']"
        ).text.split("\n")[-1]
        date = date[: date.rindex(" (")]
        try:
            date = datetime.strptime(date, "%B %d, %Y")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(date, "%B %Y")
            return date.strftime("%Y-%m")

    @data_fallback([])
    def get_origins(element) -> list[str]:
        origin_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-origin']"
        )
        origins = origin_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        origins = [o.text for o in origins]
        return origins

    @data_fallback([])
    def get_languages(element) -> list[str]:
        language_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-languages']"
        )
        languages = language_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        languages = [lang.text for lang in languages]
        return languages

    @data_fallback
    def get_imdb_rating(element) -> str:
        rating = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating']"
        ).text.split("\n")[1]
        return rating

    def get_entry(self, url, name="") -> dict:
        entry_dict = {"ImdbID": ImdbPageCrawler.get_id(url), "Name": name}
        self.__driver.get(url)
        elements = self.__driver.find_elements(By.TAG_NAME, "section")
        for e in elements:
            if attr := e.get_attribute("data-testid"):
                match attr:
                    case "atf-wrapper-bg":
                        entry_dict["Plot"] = ImdbPageCrawler.get_plot(e)
                        entry_dict["Rating"] = ImdbPageCrawler.get_imdb_rating(e)
                        entry_dict["Genres"] = ImdbPageCrawler.get_genres(e)
                        entry_dict["Runtime"] = ImdbPageCrawler.get_run_time(e)
                        entry_dict["Directors"] = ImdbPageCrawler.get_directors(e)
                    case "title-cast":
                        entry_dict["Cast"] = ImdbPageCrawler.get_cast(e)
                    case "Details":
                        entry_dict["ReleaseDate"] = ImdbPageCrawler.get_release_date(e)
                        entry_dict["OriginCountries"] = ImdbPageCrawler.get_origins(e)
                        entry_dict["Languages"] = ImdbPageCrawler.get_languages(e)
        return entry_dict
