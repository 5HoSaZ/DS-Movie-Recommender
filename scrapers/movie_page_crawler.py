from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import numpy as np
import csv
import pandas as pd
import os
import threading
from queue import Queue

NUM_CRAWLERS = 4
FIELD_NAMES = [
    "ImdbID",
    "Name",
    "Runtime",
    "ReleaseDate",
    "Directors",
    "OriginCountries",
    "Languages",
    "Genres",
    "Rating",
    "Plot",
]


class ImdbPageCrawler:
    def data_wrapper(func):
        def inner(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception:
                return None

        return inner

    def get_id(url: str):
        return url.removeprefix("https://www.imdb.com/title/")[:-1]

    @data_wrapper
    def get_directors(element):
        cast_field = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-metadata-list ipc-metadata-list--dividers-all title-pc-list ipc-metadata-list--baseAlt']",
        )
        director_field = cast_field.find_elements(
            By.CSS_SELECTOR,
            "li[class='ipc-metadata-list__item']",
        )[0]
        directors = director_field.find_elements(
            By.CSS_SELECTOR,
            "a[class='ipc-metadata-list-item__list-content-item ipc-metadata-list-item__list-content-item--link']",
        )
        return [d.text for d in directors]

    @data_wrapper
    def get_plot(element):
        return element.find_element(By.CSS_SELECTOR, "span[data-testid='plot-xl']").text

    @data_wrapper
    def get_run_time(element):
        runtime = element.find_element(
            By.CSS_SELECTOR,
            "ul[class='ipc-inline-list ipc-inline-list--show-dividers sc-ec65ba05-2 joVhBE baseAlt']",
        ).text.split("\n")[-1]
        runtime = datetime.strptime(runtime, "%Hh %Mm")
        return runtime.strftime("%H:%M:%S")

    @data_wrapper
    def get_imdb_rating(element):
        rating = element.find_element(
            By.CSS_SELECTOR, "div[data-testid='hero-rating-bar__aggregate-rating']"
        ).text.split("\n")[1]
        return rating

    @data_wrapper
    def get_genres(element):
        fields = element.find_elements(
            By.CSS_SELECTOR, "a[class='ipc-chip ipc-chip--on-baseAlt']"
        )
        genres = [f.text for f in fields]
        return genres

    @data_wrapper
    def get_release_date(element):
        date = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-releasedate']"
        ).text.split("\n")[-1]
        date = date[: date.rindex(" (")]
        try:
            date = datetime.strptime(date, "%B %d, %Y")
            return date.strftime("%Y-%m-%d")
        except ValueError:
            date = datetime.strptime(date, "%B %Y")
            return date.strftime("%Y-%m")

    @data_wrapper
    def get_origins(element):
        origin_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-origin']"
        )
        origins = origin_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        origins = [o.text for o in origins]
        return origins

    @data_wrapper
    def get_languages(element):
        language_field = element.find_element(
            By.CSS_SELECTOR, "li[data-testid='title-details-languages']"
        )
        languages = language_field.find_elements(
            By.CSS_SELECTOR, "li[class='ipc-inline-list__item']"
        )
        languages = [lang.text for lang in languages]
        return languages

    def __init__(self):
        self.option = FirefoxOptions()
        self.option.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        self.service = Service(executable_path="./drivers/firefox/geckodriver.exe")
        self.driver = webdriver.Firefox(service=self.service, options=self.option)

    def get_entry(self, url, name=""):
        entry_dict = {"ImdbID": ImdbPageCrawler.get_id(url), "Name": name}
        self.driver.get(url)
        elements = self.driver.find_elements(By.TAG_NAME, "section")
        for e in elements:
            if attr := e.get_attribute("data-testid"):
                match attr:
                    case "atf-wrapper-bg":
                        entry_dict["Plot"] = ImdbPageCrawler.get_plot(e)
                        entry_dict["Rating"] = ImdbPageCrawler.get_imdb_rating(e)
                        entry_dict["Genres"] = ImdbPageCrawler.get_genres(e)
                        entry_dict["Runtime"] = ImdbPageCrawler.get_run_time(e)
                        entry_dict["Directors"] = ImdbPageCrawler.get_directors(e)
                    case "Details":
                        entry_dict["ReleaseDate"] = ImdbPageCrawler.get_release_date(e)
                        entry_dict["OriginCountries"] = ImdbPageCrawler.get_origins(e)
                        entry_dict["Languages"] = ImdbPageCrawler.get_languages(e)
        return entry_dict

    def terminate(self):
        self.driver.quit()


def threaded(func):
    def wrapper(*args, **kwargs):
        threading.Thread(target=func, args=args, kwargs=kwargs).start()

    return wrapper


class Worker:
    def __init__(self, work_queue: Queue):
        self.queue = work_queue
        self.crawler = ImdbPageCrawler()

    def finish(self):
        self.crawler.terminate()
        self.queue.put_nowait(None)

    @threaded
    def process(self, items: pd.DataFrame):
        for _, row in items.iterrows():
            name, link = row["Name"], row["Link"]
            success = False
            while not success:
                try:
                    entry = self.crawler.get_entry(link, name)
                    success = True
                except Exception:
                    time.sleep(8)
            self.queue.put_nowait(entry)
        self.finish()


class Collector:
    def __init__(self, work_queue: Queue, worker_count: int):
        self.write_file = "./database/movie_entries.csv"
        self.queue = work_queue
        self.unfinished = worker_count

    def write(self, entry: dict):
        with open(self.write_file, "a", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=FIELD_NAMES)
            writer.writerow(entry)

    @threaded
    def process(self, item_count=1):
        count = 0
        while self.unfinished:
            item = self.queue.get()
            if item is None:
                self.unfinished -= 1
            else:
                self.write(item)
                count += 1
                print(
                    f"Processed {count}/{item_count} --- {(count / item_count):.2%}",
                    end="\r",
                )
        print("\nDone")


def split_dataframe(df, n):
    data_size = len(df)
    chunk_size = data_size // n
    return [df.iloc[i : i + chunk_size] for i in range(0, data_size, chunk_size)]


def main():
    print(f"Crawling with {NUM_CRAWLERS} crawlers.")
    # if not os.path.isfile("./database/movie_entries.csv"):
    with open("./database/movie_entries.csv", "w") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
        writer.writeheader()

    to_process = pd.read_csv("./database/movie_links.csv", encoding="latin-1")
    to_process_count = len(to_process)
    batches = split_dataframe(to_process, NUM_CRAWLERS)

    work_queue = Queue()

    for i in range(NUM_CRAWLERS):
        worker = Worker(work_queue)
        worker.process(batches[i])

    collector = Collector(work_queue, NUM_CRAWLERS)
    collector.process(to_process_count)


if __name__ == "__main__":
    main()
