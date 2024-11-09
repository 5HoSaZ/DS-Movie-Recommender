import pandas as pd

processed = pd.read_csv("./database/movieen_tries.csv", encoding="latin-1")
print(set(processed["ImdbID"].values))
