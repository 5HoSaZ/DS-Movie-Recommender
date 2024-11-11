import math
import pandas as pd
from typing import Literal, Callable, Iterable, Generator, Any
from collections import namedtuple


def get_field_names(
    website: Literal["imdb", "moviedb", "rotten_tomatoes"]
) -> list[str]:
    match website:
        case "imdb":
            return [
                "ID",
                "Name",
                "Runtime",
                "ReleaseDate",
                "Directors",
                "Cast",
                "OriginCountries",
                "Languages",
                "Genres",
                "Rating",
                "Plot",
            ]
        case "moviedb":
            return [
                "ID",
                "Name",
                "Runtime",
                "ReleaseDate",
                "Directors",
                "Cast",
                "OriginCountries",
                "Languages",
                "Genres",
                "Rating",
                "Plot",
            ]
        case "rotten_tomatoes":
            return [
                "ID",
                "Name",
                "Runtime",
                "ReleaseDate",
                "Directors",
                "Cast",
                "OriginCountries",
                "Languages",
                "Genres",
                "Rating",
                "Plot",
            ]


def get_id(website: Literal["imdb", "moviedb", "rotten_tomatoes"]) -> Callable:
    match website:
        case "imdb":
            prefix = "https://www.imdb.com/title/"
        case "moviedb":
            prefix = "https://www.themoviedb.org/"
        case "rotten_tomatoes":
            prefix = "https://www.rottentomatoes.com/m/"

    def inner(url):
        return url.removeprefix(prefix).removesuffix("/")

    return inner


def filter_processed(website: Literal["imdb", "moviedb", "rotten_tomatoes"]):
    """Return the unprocessed dataset."""
    all_links = pd.read_csv(f"./database/{website}/movie_links.csv", encoding="utf-8")
    all_id = all_links["Link"].apply(get_id(website))
    processed_id = pd.read_csv(
        f"./database/{website}/movie_entries.csv", encoding="utf-8"
    )["ID"]
    not_processed_id = set(all_id) - set(processed_id)
    return all_links.loc[all_id.isin(not_processed_id)]


MovieLink = namedtuple("MovieLink", ["Name", "Link"])
MovieLinkGenerator = Generator[MovieLink, Any, None]


def _data_generator(data: Iterable) -> MovieLinkGenerator:
    def _from_dataframe(data: pd.DataFrame):
        for _, row in data.iterrows():
            yield MovieLink(row["Name"], row["Link"])

    def _from_iterable(data: list):
        if len(data) > 0:
            assert len(data[0]) == 2, "Must contain two item per entry: 'Name', 'Link'"
        for name, link in data:
            yield MovieLink(name, link)

    if isinstance(data, pd.DataFrame):
        return _from_dataframe(data)
    elif isinstance(data, Iterable):
        return _from_iterable(data)


def split_data(data: Iterable, n: int):
    """Split the data frame as evenly as posible into generators."""
    data_size = len(data)
    chunk_size = math.ceil(data_size / n)
    if isinstance(data, pd.DataFrame):
        chunks = [
            data.iloc[i : i + chunk_size] for i in range(0, data_size, chunk_size)
        ]
    elif isinstance(data, Iterable):
        chunks = [data[i : i + chunk_size] for i in range(0, data_size, chunk_size)]
    return [_data_generator(c) for c in chunks]
