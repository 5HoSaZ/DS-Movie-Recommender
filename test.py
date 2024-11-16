from scrapers.crawlers import get_crawler
from pprint import pprint

crarw = get_crawler("imdb")

e = crarw.get_entry(92337)
pprint(e)
# print(e["Plot"])
# crarw.terminate()
