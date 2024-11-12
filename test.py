from scrapers.crawlers import get_crawler

crarw = get_crawler("imdb")

e = crarw.get_entry("https://www.imdb.com/title/tt1288461/")
print(e["Directors"])
crarw.terminate()
