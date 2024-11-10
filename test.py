from scrapers.crawlers import get_crawler

# import time
# import pandas as pd


# # url = "https://www.imdb.com/title/tt32546023/"


# # c = ImdbPageCrawler()
# # c.get_entry(url)
# # time.sleep(5)
# # c.refresh()
# # time.sleep(5)
# # c.terminate()
# def filter_processed():
#     all_links = pd.read_csv("./database/movie_links.csv")
#     all_id = all_links["Link"].apply(ImdbPageCrawler.get_id)
#     processed_id = pd.read_csv("./database/movie_entries.csv")["ImdbID"]
#     not_processed_id = set(all_id) - set(processed_id)
#     return all_links.loc[all_id.isin(not_processed_id)]


if __name__ == "__main__":
    a = get_crawler("imdb")
    print(a.get_entry("https://www.imdb.com/title/tt3469798/", "Órbita 9"))
    a.terminate()
