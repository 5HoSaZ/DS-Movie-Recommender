import pandas as pd

data = pd.read_csv("database/movie_links.csv")


def split_dataframe(df, n=5):
    data_size = len(df)
    print(data_size)
    chunk_size = data_size // n
    print(chunk_size)
    return [df.iloc[i : i + chunk_size] for i in range(0, data_size, chunk_size)]


data_splits = split_dataframe(data)
for d in data_splits:
    print(len(d))

# print(row["Name"])
print("Done")
