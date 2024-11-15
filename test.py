from scrapers.crawlers import get_crawler
from pprint import pprint

crarw = get_crawler("imdb")

e = crarw.get_entry(125877)
pprint(e)
# crarw.terminate()
