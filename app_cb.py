from models import get_recommendation, get_query, safe_load
from scrapers.drivers import Requester
from models.cb import FeatureGenerator
from utility import Mapper, Session

import os
import torch
import streamlit as st
from ast import literal_eval

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS = ["Genres+Ratings", "Titles+Plots", "Directors+Actors"]

st.title("🎥 Movie Recommendation System")

# Set up streamlit session
if "session" not in st.session_state:
    # Import dataset and mapper
    api_key = None
    if os.path.isfile("./scrapers/drivers/moviedb.txt"):
        with open("./scrapers/drivers/moviedb.txt", "r") as file:
            api_key = file.readline()
    session = Session("cb", Requester(api_key))
    session.mapper = Mapper.load("./database/merged/mapper.pkl")
    st.success("Set up new session successfully!")
else:
    session = st.session_state.session
    st.success("Fetching past session data")

# Setup recommender
recommender = get_recommendation("cb", 10, DEVICE)

# Select model for recommendation
with st.sidebar:
    current_model = st.selectbox("Select models:", MODELS)
    if session.model_name != current_model:
        match current_model:
            case "Genres+Ratings":
                weights = safe_load("./models/cb/genres_with_ratings.pt", DEVICE)
            case "Titles+Plots":
                weights = safe_load("./models/cb/titles_and_plots.pt", DEVICE)
            case "Directors+Actors":
                weights = safe_load("./models/cb/directors_and_cast.pt", DEVICE)
        session.model_name = current_model
        session.model = FeatureGenerator(weights)
st.success("Model loaded successfully!")


# Function to generate recommendations
def generate_recommendations(session: Session, movie_id: int):
    try:
        movie_idx = session.mapper.item_fwd_map[movie_id]
        idxs, sims = recommender(movie_idx, session.model)
    except KeyError:
        idxs = []
        sims = []
    recommended_movies = get_query(session.movies, session.mapper, idxs)
    recommended_movies = recommended_movies.assign(Similarity=sims)
    return recommended_movies


# Input box for Movie ID and number of recommendations
st.write("Find your next favorite movie based on your preferences!")
with st.sidebar:
    # Drop down to get movie id by title
    movie_ids = session.movies["MovieID"]
    movie_titles = session.movies["Title"]
    selected_id = st.selectbox(
        "Select a Movie to View Details:",
        range(len(movie_titles)),
        format_func=movie_titles.__getitem__,
    )
    movie_id = movie_ids[selected_id]
    movie_title = movie_titles[selected_id]

    # Option for number of recommendations
    count = st.number_input("Number of recommendation:", min_value=1, step=1, value=10)
    recommender = get_recommendation("cb", count, DEVICE)

# Get selected movie detail
movie_details = session.movies[session.movies["MovieID"] == movie_id].iloc[0]
st.subheader(f"🎥 {movie_details['Title']}")

cols = st.columns([1, 2])

with cols[0]:
    # Fetch poster image
    if movie_id != session.query:
        session.query = movie_id
        session.image_path = session.get_poster_path(movie_id)
    # Display poster image
    if session.image_path:
        st.image(session.image_path, use_container_width=True)
    else:
        st.text("No Poster Available")

with cols[1]:
    st.markdown(f"**MovieID**: {movie_id}")
    st.markdown(f"**Genres**: {", ".join(literal_eval(movie_details['Genres']))}")
    st.markdown(f"**Runtime**: {movie_details['Runtime']}")
    st.markdown(f"**Release Date**: {movie_details['ReleaseDate']}")
    st.markdown(f"**Rating**: {movie_details['AverageRating']}")
    st.markdown(f"**Plot**: {movie_details['Plot']}")
    st.markdown(f"**Directors**: {", ".join(literal_eval(movie_details['Directors']))}")
    st.markdown(f"**Cast**: {", ".join(literal_eval(movie_details['Cast'])[:5])}")
st.markdown("---")

# Get recommendation
with st.sidebar:
    recommend_button = st.button("Get Recommendations")

if recommend_button:
    # Show the recommended movies based on the selected movie
    recommended_movies = generate_recommendations(session, movie_id)
    if recommended_movies is not None and not recommended_movies.empty:
        # Display the results
        st.write(f"### Recommended Movies for '{movie_title}':")
        for _, row in recommended_movies.iterrows():
            st.subheader(f"🎥 {row['Title']}")
            st.write(f"**MovieID**: {row['MovieID']}")
            match session.model_name:
                case "Genres+Ratings":
                    st.write(f"**Genres**: {", ".join(literal_eval(row['Genres']))}")
                case "Titles+Plots":
                    st.write(f"**Plot**: {row['Plot']}")
                case "Directors+Actors":
                    st.write(
                        f"**Directors**: {", ".join(literal_eval(row['Directors']))}"
                    )
                    st.write(f"**Cast**: {", ".join(literal_eval(row['Cast'])[:5])}")
            st.write(f"**Similarity**: {row['Similarity']:.2f}")
            st.write("---")
    else:
        st.write("No recommendations available.")
st.session_state.session = session
