from scrapers.crawlers import get_crawler
from pprint import pprint

crarw = get_crawler("tmdb")

e = crarw.get_entry(1166713)
pprint(e)
# print(e["Plot"])
# crarw.terminate()
