import torch
import torch.nn as nn


class EmbededRatingNet(nn.Module):

    def __init__(self, num_user: int, num_item: int, num_factors=8):
        super(EmbededRatingNet, self).__init__()
        self.user_embedding = nn.Embedding(num_user, num_factors, sparse=True)
        self.item_embedding = nn.Embedding(num_item, num_factors, sparse=True)
        self.dense1 = nn.Linear(num_factors * 2, 32)
        self.dense2 = nn.Linear(32, 4)
        self.out = nn.Linear(4, 1, dtype=torch.float32)
        self.relu = nn.ReLU()

    def __call__(self, user, item):
        user_embedded = self.user_embedding(user)
        item_embedded = self.item_embedding(item)
        x = torch.cat([user_embedded, item_embedded], dim=1)
        x = self.relu(self.dense1(x))
        x = self.relu(self.dense2(x))
        return self.out(x)


class EmbededDotNet(nn.Module):

    def __init__(self, num_user: int, num_item: int, num_factors=8):
        super(EmbededDotNet, self).__init__()
        self.user_embedding = nn.Embedding(num_user, num_factors, sparse=True)
        self.item_embedding = nn.Embedding(num_item, num_factors, sparse=True)
        self.flatten = nn.Flatten()

    def __call__(self, user, item):
        user_embedded = self.flatten(self.user_embedding(user))
        item_embedded = self.flatten(self.item_embedding(item))
        x = (user_embedded * item_embedded).sum(dim=1)
        return x.unsqueeze(1)
