from models import get_recommendation, get_query
from models.hybrid import EmbededHybridNet
from utility import Mapper

import torch
import streamlit as st
import pandas as pd
from ast import literal_eval

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Set up streamlit
st.title("🎬 Movie Recommendation System")

# Import dataset and mapper
metadatas = pd.read_csv("./database/merged/metadatas.csv")
movie_ratings = pd.read_csv("./database/merged/global_ratings.csv")
movies = pd.merge(metadatas, movie_ratings, on="MovieID")
ui_ratings = pd.read_csv("./database/merged/full/ratings.csv")
full_mapper = Mapper.load("./database/merged/mapper.pkl")
st.success("Data loaded successfully!")

# Using Hybrid model for recommendation
num_users = len(full_mapper.user_fwd_map)
num_items = len(full_mapper.item_fwd_map)
hybrid = EmbededHybridNet(
    num_users,
    torch.load(
        "./models/cb/genres_with_ratings.pt", map_location=DEVICE, weights_only=True
    ),
    torch.load(
        "./models/cb/titles_and_plots.pt", map_location=DEVICE, weights_only=True
    ),
    torch.load(
        "./models/cb/directors_and_cast.pt", map_location=DEVICE, weights_only=True
    ),
)
hybrid.load_state_dict(
    torch.load(
        "./models/hybrid/embedded_hybrid.pth", map_location=DEVICE, weights_only=True
    )
)
st.success("Model loaded successfully!")

# Setup recommender
recommender = get_recommendation("cf", 10, DEVICE)


# Function to generate recommendations
def generate_recommendations(user_id: int, excludes):
    try:
        user_idx = full_mapper.user_fwd_map[user_id]
        idxs, ratings = recommender(user_idx, num_items, hybrid, excludes=excludes)
    except KeyError:
        idxs = []
        ratings = []
    recommended_movies = get_query(movies, full_mapper, idxs)
    recommended_movies = recommended_movies.assign(Predicted_Rating=ratings)
    return recommended_movies


st.write("Enter a User ID to get personalized movie recommendations!")

# Input box for User ID
user_id = st.number_input("Enter User ID:", min_value=0, step=1, value=123)
user_rated = [
    full_mapper.item_fwd_map[i]
    for i in ui_ratings[ui_ratings["UserID"] == user_id]["MovieID"]
]

if st.button("Get Recommendations"):
    st.write(f"Fetching recommendations for User ID: {user_id}...")
    recommended_movies = generate_recommendations(user_id, user_rated)
    if recommended_movies is not None and not recommended_movies.empty:
        # Display the results
        st.write("### Recommended Movies:")
        for _, row in recommended_movies.iterrows():
            st.subheader(f"🎥 {row['Title']}")
            st.write(f"**MovieID**: {row['MovieID']}")
            st.write(f"**Genres**: {", ".join(literal_eval(row['Genres']))}")
            st.write(f"**Predicted Rating**: {row['Predicted_Rating']:.2f}")
            st.write("---")
    elif recommended_movies is not None:
        st.warning("No recommendations found for this user.")
