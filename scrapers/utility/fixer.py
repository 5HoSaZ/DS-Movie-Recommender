import pandas as pd


# data[data["ReleaseDate"] is None]
def filter_null():
    data = pd.read_csv("./database/imdb/movie_entries.csv", encoding="utf-8")
    f_data = data[data["ReleaseDate"].notnull()]
    f_data.to_csv("./database/imdb/movie_entries.csv", index=False)
    print("Done")

def fix_encoding()
    links = pd.read_csv("./backup/imdb/movie_links copy.csv", encoding="utf-8")
    print(len(links))
    mapping = {
        row["Link"]
        .removeprefix("https://www.imdb.com/title/")
        .removesuffix("/"): row["Name"]
        for _, row in links.iterrows()
    }

    def replace(row):
        return mapping[row["ID"]]

    entries = pd.read_csv("./backup/imdb/movie_entries copy.csv", encoding="utf-8")
    entries["Name"] = entries.apply(lambda row: replace(row), axis=1)
    entries.to_csv(
        "./backup/imdb/movie_entries copy.csv", encoding="utf-8", index=False
    )

if __name__ == "__main__":
    fix_encoding()
