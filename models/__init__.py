import torch
import torch.nn as nn
from .cb import FeatureGenerator


class EmbededHybridNet(nn.Module):

    def __init__(self, num_user: int, genres, titles_and_plots, directors_and_casts):
        super(EmbededHybridNet, self).__init__()
        # Item features
        self.item_weighted_genres = FeatureGenerator(genres)
        self.item_titles_plots = FeatureGenerator(titles_and_plots)
        self.item_directors_casts = FeatureGenerator(directors_and_casts)
        # User features
        self.user_weighted_genres = nn.Embedding(
            num_user, self.item_weighted_genres.num_feature, sparse=True
        )
        self.user_titles_plots = nn.Embedding(
            num_user, self.item_titles_plots.num_feature, sparse=True
        )
        self.user_directors_casts = nn.Embedding(
            num_user, self.item_directors_casts.num_feature, sparse=True
        )
        # Features dense layers
        self.dense_weighted_genres = nn.Linear(
            self.item_weighted_genres.num_feature * 2, 2
        )
        self.dense_titles_plots = nn.Linear(self.item_titles_plots.num_feature * 2, 2)
        self.dense_directors_casts = nn.Linear(
            self.item_directors_casts.num_feature * 2, 2
        )
        # Dense
        self.out = nn.Linear(6, 1, dtype=torch.float32)
        # Relu
        self.relu = nn.ReLU()

    def __call__(self, user, item):
        # Weighted genres
        user_weighted_genres = self.user_weighted_genres(user)
        item_weighted_genres = self.item_weighted_genres(item)
        weighted_genres = torch.cat([user_weighted_genres, item_weighted_genres], dim=1)
        weighted_genres = self.dense_weighted_genres(weighted_genres)
        # Tiltes and plots
        user_titles_plots = self.user_titles_plots(user)
        item_titles_plots = self.item_titles_plots(item)
        titles_plots = torch.cat([user_titles_plots, item_titles_plots], dim=1)
        titles_plots = self.dense_titles_plots(titles_plots)
        # Directors and casts
        user_directors_casts = self.user_directors_casts(user)
        item_directors_casts = self.item_directors_casts(item)
        directors_casts = torch.cat([user_directors_casts, item_directors_casts], dim=1)
        directors_casts = self.dense_directors_casts(directors_casts)
        # Final denses
        x = self.relu(
            torch.cat([weighted_genres, titles_plots, directors_casts], dim=1)
        )
        return self.out(x)
