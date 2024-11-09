from scrapers import ImdbPageCrawler

crawler = ImdbPageCrawler()
e = crawler.get_entry("https://www.imdb.com/title/tt27403986/")
crawler.terminate()
