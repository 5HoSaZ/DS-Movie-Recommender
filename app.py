import sys
import os

from models import get_recommendation, get_query
from models.hybrid import EmbededHybridNet
from utility import Mapper

import torch
from typing import Iterable
import streamlit as st
import pandas as pd
import ast


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Set up streamlit
st.title("🎬 Movie Recommendation System")

# Import dataset and mapper
metadatas = pd.read_csv("./database/merged/metadatas.csv")
movie_ratings = pd.read_csv("./database/merged/global_ratings.csv")
movies = pd.merge(metadatas, movie_ratings, on="MovieID")
full_mapper = Mapper.load("./database/merged/mapper.pkl")
st.success("Data loaded successfully!")

# Using Hybrid model for recommendation
num_users = len(full_mapper.user_fwd_map)
num_items = len(full_mapper.item_fwd_map)
hybrid = EmbededHybridNet(
    num_users,
    torch.load("./models/cb/genres_with_ratings.pt"),
    torch.load("./models/cb/titles_and_plots.pt"),
    torch.load("./models/cb/directors_and_cast.pt"),
)
hybrid.load_state_dict(torch.load("./models/hybrid/embedded_hybrid.pth"))
st.success("Model loaded successfully!")

# Setup recommender
recommender = get_recommendation("cf", 10, DEVICE)


# Function to generate recommendations
def generate_recommendations(user_id: int):
    try:
        user_idx = full_mapper.user_fwd_map[user_id]
        idxs, ratings = recommender(user_idx, num_items, hybrid)
    except KeyError:
        idxs = []
    recommended_movies = get_query(movies, full_mapper, idxs)
    return recommended_movies
    # recommended_movies = recommended_movies.assign(Predicted_Rating=ratings.numpy())


st.write("Enter a User ID to get personalized movie recommendations!")

# Input box for User ID
user_id = st.number_input("Enter User ID:", min_value=0, step=1, value=123)

if st.button("Get Recommendations"):
    print("Aa")
    st.write(f"Fetching recommendations for User ID: {user_id}...")
    recommended_movies = generate_recommendations(user_id)
    print(recommended_movies)

    # if recommended_movies is not None and not recommended_movies.empty:
    #     # Display the results
    #     st.write("### Recommended Movies:")
    #     for _, row in recommended_movies.iterrows():
    #         st.subheader(f"🎥 {row['Title']}")
    #         st.write(f"**Genres**: {row['Genres']}")
    #         st.write(f"**Predicted Rating**: {row['Predicted_Rating']:.2f}")
    #         st.write("---")
    # elif recommended_movies is not None:
    #     st.warning("No recommendations found for this user.")
