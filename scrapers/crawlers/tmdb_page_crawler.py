from .interface import PageCrawler
from ..drivers import Requester
from ..utility.data import get_field_names
from ..utility.wrapper import data_fallback


class TmdbPageCrawler(PageCrawler):
    FIELD_NAMES = get_field_names("tmdb")

    def __init__(self):
        self.__requester = Requester()

    def restart(self) -> None:
        return

    def terminate(self) -> None:
        return

    @data_fallback(None)
    def _get_rating(response: dict) -> str:
        return response["vote_average"]

    @data_fallback(None)
    def _get_vote_count(response: dict) -> str:
        return response["vote_count"]

    @data_fallback([])
    def _get_directors(response: dict) -> list[str]:
        crews = response["credits"]["crew"]
        return [c["name"] for c in crews if c["job"] == "Director"]

    @data_fallback([])
    def _get_cast(response: dict) -> list[str]:
        casts = response["credits"]["cast"]
        return [c["name"] for c in casts]

    @data_fallback(None)
    def _get_plot(response: dict) -> str:
        return response["overview"]

    @data_fallback(None)
    def _get_run_time(response: dict) -> str:
        runtime = response["runtime"]  # Minutes
        hours, minutes = runtime // 60, runtime % 60
        return f"{hours:02d}:{minutes:02d}:00"

    @data_fallback([])
    def _get_genres(response: dict) -> list[str]:
        genres = response["genres"]
        return [g["name"] for g in genres]

    @data_fallback([])
    def _get_origins(response: dict) -> list[str]:
        return response["origin_country"]

    @data_fallback(None)
    def _get_release_date(response: dict) -> str:
        return response["release_date"]

    @data_fallback([])
    def _get_languages(response: dict) -> list[str]:
        languages = response["spoken_languages"]
        return [l["english_name"] for l in languages]

    def get_entry(self, tmdb_id: int) -> dict:
        entry_dict = {"TmdbID": tmdb_id}
        url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?append_to_response=credits&language=en-US"
        response = self.__requester.get(url)
        entry_dict["Rating"] = TmdbPageCrawler._get_rating(response)
        entry_dict["VoteCount"] = TmdbPageCrawler._get_vote_count(response)
        entry_dict["Runtime"] = TmdbPageCrawler._get_run_time(response)
        entry_dict["Genres"] = TmdbPageCrawler._get_genres(response)
        entry_dict["Directors"] = TmdbPageCrawler._get_directors(response)
        entry_dict["Cast"] = TmdbPageCrawler._get_cast(response)
        entry_dict["ReleaseDate"] = TmdbPageCrawler._get_release_date(response)
        entry_dict["OriginCountries"] = TmdbPageCrawler._get_origins(response)
        entry_dict["Languages"] = TmdbPageCrawler._get_languages(response)
        entry_dict["Plot"] = TmdbPageCrawler._get_plot(response)
        return entry_dict
