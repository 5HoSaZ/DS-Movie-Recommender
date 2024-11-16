from scrapers.drivers import Requester

import pandas as pd


def main():
    converter = Requester()
    links = pd.read_csv("./database/ml-32m/links.csv")
    missing = links[links["tmdbId"].isna()]
    missing_count = len(missing)
    for i, idx in enumerate(missing.index):
        imdb_id = int(links.iloc[idx]["imdbId"])
        url = (
            f"https://api.themoviedb.org/3/find/tt{imdb_id:07d}?external_source=imdb_id"
        )
        results = converter.get(url)["movie_results"]
        if results:
            tmdb_id = results[0]["id"]
        else:
            tmdb_id = None
        print(f"{i + 1}/{missing_count}: {imdb_id} --> {tmdb_id}")
        links.loc[int(idx), "tmdbId"] = tmdb_id
    links.to_csv("./database/ml-32m/links.csv", index=False)


if __name__ == "__main__":
    main()
