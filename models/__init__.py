from .cb import FeatureGenerator
from .cf import EmbededDotNet, EmbededRatingNet
from .hybrid import EmbededHybridNet

import torch
from functools import partial
from typing import Literal

CFNet = EmbededDotNet | EmbededRatingNet | EmbededHybridNet


def get_recommendation(mode: Literal["cb", "cf"], top: int = 10, device="cpu"):
    match mode:
        case "cb":
            return partial(__get_cb_recommendation, top=top, device=device)
        case "cf":
            return partial(__get_cf_recommendation, top=top, device=device)


def __get_cb_recommendation(movie, model: FeatureGenerator, top, device):
    model = model.to(device)
    movie_ids, sim_scores = model.get_top_similar(movie, top)
    return movie_ids, sim_scores


def __get_cf_recommendation(user, num_items, model: CFNet, top, device, excludes=[]):
    model = model.to(device).eval()
    users = torch.tensor([user] * num_items, dtype=torch.int64, device=device)
    movies = torch.tensor(range(num_items), dtype=torch.int64, device=device)
    with torch.no_grad():
        ratings = torch.flatten(model(users, movies))
    values, indices = torch.sort(ratings, descending=True)
    valid = torch.isin(indices, torch.tensor(excludes), invert=True)
    values = values[valid][:top].cpu()
    indices = indices[valid][:top].cpu()
    return indices, values


def get_query(movie_data, mapper, indices):
    movie_ids = [mapper.item_inv_map[int(i)] for i in indices]
    return movie_data[movie_data["MovieID"].isin(movie_ids)]
