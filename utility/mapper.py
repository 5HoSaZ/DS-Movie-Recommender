from __future__ import annotations
import numpy as np
import pickle as pkl


class Mapper:

    def __init__(self, ui_mat):
        users, items = np.transpose(ui_mat)
        u_user, u_item = np.unique(users), np.unique(items)
        n_user, n_item = len(u_user), len(u_item)
        self.user_fwd_map = {int(user): uid for user, uid in zip(u_user, range(n_user))}
        self.user_inv_map = {uid: user for user, uid in self.user_fwd_map.items()}
        self.item_fwd_map = {int(item): uid for item, uid in zip(u_item, range(n_item))}
        self.item_inv_map = {uid: item for item, uid in self.item_fwd_map.items()}

    def save(self, file):
        with open(file, "wb") as f:
            pkl.dump(self, f)

    def load(file) -> Mapper:
        with open(file, "rb") as f:
            return pkl.load(f)
