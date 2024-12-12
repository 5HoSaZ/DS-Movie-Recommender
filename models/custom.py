from __future__ import annotations
from torch.utils.data import Dataset

import os
import random
import numpy as np
import pandas as pd


def _get_index_split(size: int, frac: float, seed=None):
    cap = int(size * frac)
    indexes = list(range(size))
    random.seed(seed)
    random.shuffle(indexes)
    return indexes[:cap], indexes[cap:]


class RatingDataset(Dataset):
    """Custom dataset for ratings"""

    RATING_FILE = "ratings.csv"

    def __init__(self, data: str | pd.DataFrame, mapper=None, normalize=False):
        if isinstance(data, str):
            self.dataset = pd.read_csv(os.path.join(data, self.RATING_FILE))
        elif isinstance(data, pd.DataFrame):
            self.dataset = data
        self.mapper = mapper
        self.normalize = normalize

    def __len__(self):
        return len(self.dataset)

    def split(
        self, train_proportion: float, seed=None
    ) -> tuple[RatingDataset, RatingDataset]:
        s1, s2 = _get_index_split(len(self), train_proportion, seed)
        train = RatingDataset(
            self.dataset.iloc[s1].reset_index(drop=True), self.mapper, self.normalize
        )
        valid = RatingDataset(
            self.dataset.iloc[s2].reset_index(drop=True), self.mapper, self.normalize
        )
        return train, valid

    def __getitem__(self, idx) -> tuple[int, int, float]:
        row = self.dataset.iloc[idx]
        user = int(row["UserID"])
        movie = int(row["MovieID"])
        rating = float(row["Rating"])
        if self.mapper:
            user = self.mapper.user_fwd_map[user]
            movie = self.mapper.item_fwd_map[movie]
        if self.normalize:
            rating /= 5
        return user, movie, np.float32(rating)
