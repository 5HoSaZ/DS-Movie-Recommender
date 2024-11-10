import pandas as pd

# data[data["ReleaseDate"] is None]
if __name__ == "__main__":
    data = pd.read_csv("./database/imdb/movie_entries.csv")
    f_data = data[data["ReleaseDate"].notnull()]
    f_data.to_csv("./database/imdb/movie_entries.csv", index=False)
    print("Done")
