from utility import Mapper, prune_bigraph
import pandas as pd
import os
import numpy as np

SOURCE_FILE = "./database/merged/full/ratings.csv"
TARGET_FILE = "./database/merged/small/ratings.csv"
SOURCE_MAPPER_FILE = "./database/merged/full/pydata/mapper.pkl"
TARGET_MAPPER_FILE = "./database/merged/small/pydata/mapper.pkl"
print("Loading data...")
ratings = pd.read_csv(SOURCE_FILE)
user_items = ratings.drop(columns="Rating").to_numpy()
if not os.path.isfile(SOURCE_MAPPER_FILE):
    print("Creating mapper...")
    mapper = Mapper(user_items)
    mapper.save(SOURCE_MAPPER_FILE)
else:
    print("Loading mapper...")
    mapper = Mapper.load(SOURCE_MAPPER_FILE)

users, items = user_items.T
num_user, num_item = len(np.unique(users)), len(np.unique(items))
print("Mapping...")
users = iter([mapper.user_fwd_map[int(u)] for u in users])
items = iter([mapper.item_fwd_map[int(i)] for i in items])
print("Start bigraph pruning...")
valid_users, valid_items = prune_bigraph(
    a=users, b=items, counts=(num_user, num_item), thresholds=(100, 100)
)
print("Inverse Mapping...")
valid_users = [mapper.user_inv_map[u] for u in valid_users]
valid_items = [mapper.item_inv_map[i] for i in valid_items]
print("Reducing...")
reduced_ratings = ratings[
    (ratings["UserID"].isin(valid_users)) & (ratings["MovieID"].isin(valid_items))
]
print("Saving...")
reduced_ratings.to_csv(TARGET_FILE, index=False)
mapper = Mapper(reduced_ratings.drop(columns="Rating").to_numpy())
mapper.save(TARGET_MAPPER_FILE)
print("Done")
