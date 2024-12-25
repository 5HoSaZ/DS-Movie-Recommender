from typing import Literal
import pandas as pd


class Session:
    def __init__(self, task: Literal["cb", "cf"], requester=None):
        # Set up movie data
        metadatas = pd.read_csv("./database/merged/metadatas.csv")
        movie_ratings = pd.read_csv("./database/merged/global_ratings.csv")
        self.movies: pd.DataFrame = pd.merge(metadatas, movie_ratings, on="MovieID")
        # Set up ratings for cf task
        if task == "cf":
            self.ui_ratings = pd.read_csv("./database/merged/full/ratings.csv")
        # Set up requester to get movie poster
        self.requester = requester
        if requester is not None:
            self.links = pd.read_csv("./database/ml-32m/links.csv")
        # Mapper and model place holder
        self.mapper = ...
        self.model_name = ...
        self.model = ...
        # Session query
        self.query = None
        self.image_path = None

    def get_poster_path(self, movie_id: int) -> str | None:
        if self.requester is not None:
            try:
                tmdb_id = int(
                    self.links["TmdbID"][self.links["MovieID"] == movie_id].iloc[0]
                )
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                res = self.requester.get(url, 1.0)
                poster_path = res.get("poster_path", None)
                if poster_path is not None:
                    poster_path = "https://image.tmdb.org/t/p/w500" + poster_path
                return poster_path
            except Exception as e:
                print("Error getting poster")
                print(e)

    @property
    def num_users(self) -> int:
        return len(self.mapper.user_fwd_map)

    @property
    def num_items(self) -> int:
        return len(self.mapper.item_fwd_map)
