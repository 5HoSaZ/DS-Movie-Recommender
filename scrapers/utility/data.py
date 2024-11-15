import math
import pandas as pd
from typing import Literal, Iterable, Generator, Any
from collections import namedtuple


def get_field_names(website: Literal["imdb", "tmdb"]) -> list[str]:
    match website:
        case "imdb":
            return [
                "ImdbID",
                "Runtime",
                "ReleaseDate",
                "Rating",
                "VoteCount",
                "Directors",
                "Cast",
                "OriginCountries",
                "Languages",
                "Genres",
                "Plot",
            ]
        case "tmdb":
            return [
                "TmdbID",
                "Runtime",
                "ReleaseDate",
                "Rating",
                "VoteCount",
                "Directors",
                "Cast",
                "OriginCountries",
                "Languages",
                "Genres",
                "Plot",
            ]


def filter_processed(website: Literal["imdb", "tmdb"]):
    """Return the unprocessed dataset."""
    all_links = pd.read_csv("./database/ml-32m/links.csv")
    processed = pd.read_csv(f"./database/{website}/movie_entries.csv")
    match website:
        case "imdb":
            all_ids = all_links["imdbId"]
            processed_ids = processed["ImdbID"]
        case "tmdb":
            all_ids = all_links["tmdbId"]
            processed_ids = processed["TmdbID"]
    return all_ids.loc[~all_ids.isin(processed_ids)]


MovieID = namedtuple("MovieID", ["ID"])
MovieIDGenerator = Generator[MovieID, Any, None]


def _data_generator(data: Iterable) -> MovieIDGenerator:
    def _from_dataframe(data: pd.DataFrame):
        for _, row in data.iterrows():
            yield MovieID(row)

    def _from_iterable(data: list):
        for movie_id in data:
            yield MovieID(movie_id)

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

    if len(chunks) < n:
        chunks.extend([[] for _ in range(n - len(chunks))])
    return [_data_generator(c) for c in chunks]


if __name__ == "__main__":
    website = "imdb"
    print(f"Website: {website}")
    f = filter_processed(website)
    print(len(f))
    s = split_data(f, 5)
    [print(next(s[0])) for _ in range(10)]
