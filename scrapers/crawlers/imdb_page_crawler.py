from .interface import PageCrawler, By
from ..utility.data import get_id, get_field_names
from ..utility.wrapper import data_fallback

from datetime import datetime


class ImdbPageCrawler(PageCrawler):
    FIELD_NAMES = get_field_names("imdb")

    def _get_id(url) -> str:
        return get_id("imdb")(url)

    @data_fallback([])
    def _get_directors(element) -> list[str]:
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
        runtime = datetime.strptime(runtime, "%Hh %Mm")
        return runtime.strftime("%H:%M:%S")

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
        rformats = ["%Y-%m-%d", "%B %Y", "%Y"]
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
    def _get_release_date_fallback(element) -> str:
        date = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']",
        ).text.split("\n")[0]
        return date

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

    @data_fallback(None)
    def get_imdb_rating(element) -> str:
        rating = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating']"
        ).text.split("\n")[1]
        return rating

    def get_entry(self, url, name="") -> dict:
        entry_dict = {"ID": ImdbPageCrawler._get_id(url), "Name": name}
        self._driver.get(url)
        elements = self._driver.find_elements(By.TAG_NAME, "section")
        rdate_fallback = None
        for e in elements:
            if attr := e.get_attribute("data-testid"):
                match attr:
                    case "atf-wrapper-bg":
                        entry_dict["Plot"] = ImdbPageCrawler._get_plot(e)
                        entry_dict["Rating"] = ImdbPageCrawler.get_imdb_rating(e)
                        entry_dict["Genres"] = ImdbPageCrawler._get_genres(e)
                        entry_dict["Runtime"] = ImdbPageCrawler._get_run_time(e)
                        entry_dict["Directors"] = ImdbPageCrawler._get_directors(e)
                        rdate_fallback = ImdbPageCrawler._get_release_date_fallback(e)
                    case "title-cast":
                        entry_dict["Cast"] = ImdbPageCrawler._get_cast(e)
                    case "Details":
                        entry_dict["ReleaseDate"] = (
                            ImdbPageCrawler._get_release_date(e) or rdate_fallback
                        )
                        entry_dict["OriginCountries"] = ImdbPageCrawler._get_origins(e)
                        entry_dict["Languages"] = ImdbPageCrawler._get_languages(e)
        return entry_dict
