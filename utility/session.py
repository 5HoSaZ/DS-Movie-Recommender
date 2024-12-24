from typing import Literal
import pandas as pd


class Session:
    def __init__(self, task: Literal["cb", "cf"], include_links=False):
        # Set up movie data
        metadatas = pd.read_csv("./database/merged/metadatas.csv")
        movie_ratings = pd.read_csv("./database/merged/global_ratings.csv")
        self.movies: pd.DataFrame = pd.merge(metadatas, movie_ratings, on="MovieID")
        # Set up ratings for cf task
        if task == "cf":
            self.ui_ratings = pd.read_csv("./database/merged/full/ratings.csv")
        if include_links:
            self.links = pd.read_csv("./database/ml-32m/links.csv")
        # Mapper and model place holder
        self.mapper = ...
        self.model_name = ...
        self.model = ...

    @property
    def num_users(self) -> int:
        return len(self.mapper.user_fwd_map)

    @property
    def num_items(self) -> int:
        return len(self.mapper.item_fwd_map)
