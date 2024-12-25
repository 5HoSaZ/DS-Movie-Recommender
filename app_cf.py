from models import get_recommendation, get_query, safe_load
from models.cf import EmbededRatingNet, EmbededDotNet
from models.hybrid import EmbededHybridNet
from utility import Mapper, Session

import torch
import streamlit as st
from ast import literal_eval


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS = ["EmbeddedDotNet", "EmbededRatingNet", "EmbededHybridNet"]

st.title("🎬 Movie Recommendation System")

# Set up streamlit session
if "session" not in st.session_state:
    # Import dataset
    session = Session("cf")
    st.success("Set up new session successfully!")
else:
    session = st.session_state.session
    st.success("Fetching past session data")

# Setup recommender
recommender = get_recommendation("cf", 10, DEVICE)

# Select model for recommendation
with st.sidebar:
    current_model = st.selectbox("Select models:", MODELS)
    if session.model_name != current_model:
        match current_model:
            case "EmbeddedDotNet":
                session.mapper = Mapper.load("./database/merged/full/pydata/mapper.pkl")
                model = EmbededDotNet(session.num_users, session.num_items, 10)
                weights = safe_load("./models/cf/embedded_dot_10.pth", DEVICE)
            case "EmbededRatingNet":
                session.mapper = Mapper.load("./database/merged/full/pydata/mapper.pkl")
                model = EmbededRatingNet(session.num_users, session.num_items, 8)
                weights = safe_load("./models/cf/embedded_rating_8.pth", DEVICE)
            case "EmbededHybridNet":
                session.mapper = Mapper.load("./database/merged/mapper.pkl")
                model = EmbededHybridNet(
                    session.num_users,
                    safe_load("./models/cb/genres_with_ratings.pt", DEVICE),
                    safe_load("./models/cb/titles_and_plots.pt", DEVICE),
                    safe_load("./models/cb/directors_and_cast.pt", DEVICE),
                )
                weights = safe_load("./models/hybrid/embedded_hybrid.pth", DEVICE)
        session.model_name = current_model
        model.load_state_dict(weights)
        session.model = model
st.success("Model loaded successfully!")


# Function to generate recommendations
def generate_recommendations(session: Session, user_id: int, excludes):
    try:
        user_idx = session.mapper.user_fwd_map[user_id]
        idxs, ratings = recommender(
            user_idx,
            session.num_items,
            session.model,
            excludes=excludes,
        )
    except KeyError:
        idxs = []
        ratings = []
    recommended_movies = get_query(session.movies, session.mapper, idxs)
    recommended_movies = recommended_movies.assign(Predicted_Rating=ratings)
    return recommended_movies


# Input box for User ID and number of recommendations
st.write("Enter a User ID to get personalized movie recommendations!")
with st.sidebar:
    user_id = st.number_input("Enter User ID:", min_value=0, step=1, value=123)
    user_rated = [
        session.mapper.item_fwd_map[i]
        for i in session.ui_ratings[session.ui_ratings["UserID"] == user_id]["MovieID"]
    ]
    count = st.number_input("Number of recommendation:", min_value=1, step=1, value=10)
    recommender = get_recommendation("cf", count, DEVICE)

# Get recommendation
with st.sidebar:
    recommend_button = st.button("Get Recommendations")

if recommend_button:
    st.write(f"Fetching recommendations for User ID: {user_id}...")
    recommended_movies = generate_recommendations(session, user_id, user_rated)
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
st.session_state.session = session
