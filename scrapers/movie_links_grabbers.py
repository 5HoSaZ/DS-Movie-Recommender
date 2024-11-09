from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import time
import math
import pandas as pd
import csv

FIELD_NAMES = ["Index", "Name", "Link"]


class ImdbLinkGrabber:
    item_index = 0

    def __init__(self):
        self.__option = FirefoxOptions()
        self.__option.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
        self.__service = Service(executable_path="./drivers/firefox/geckodriver.exe")
        self.__driver = webdriver.Firefox(service=self.__service, options=self.__option)

    # Get the total of movie found
    def __get_movie_count(self) -> int:
        try:
            count_field = self.__driver.find_element(
                By.CLASS_NAME, "sc-13add9d7-3.fwjHEn"
            )
            count = int(count_field.text.split(" ")[-1].replace(",", ""))
            return count
        except Exception:
            return 0

    def scroll_down(self):
        self.__driver.execute_script(
            """
            var scrollingElement = (document.scrollingElement || document.body);
            scrollingElement.scrollTop = scrollingElement.scrollHeight;
            """
        )
        # Wait to load
        time.sleep(1.2)

    # Action perform to load more movies on browser
    def __get_50_more(self):
        success = False
        sleep_time = 0
        while not success:
            try:
                self.scroll_down()
                next_50_button = self.__driver.find_element(
                    By.CLASS_NAME, "ipc-see-more__text"
                )
                next_50_button.click()
            except Exception:
                sleep_time += 1
                time.sleep(sleep_time)
                continue
            success = True
            time.sleep(1)

    def terminate(self):
        self.__driver.quit()

    def grab_links(self, url) -> list[dict]:
        # Connect to url
        self.__driver.get(url)
        movie_count = self.__get_movie_count()
        print(f"Scraper found {movie_count} movies from {url}.")
        # Loading movies
        for i in range(load_count := (math.ceil(movie_count / 50) - 1)):
            print(f"Loading items: {i + 1}/{load_count}", end="\r")
            self.__get_50_more()
        print()
        self.scroll_down()
        # Find all movies
        items = self.__driver.find_elements(By.CLASS_NAME, "ipc-title-link-wrapper")
        links = []

        for item in items:
            self.item_index += 1
            # Get index and name
            index, name = item.text.split(". ", maxsplit=1)
            # Get movie link
            link = item.get_attribute("href")
            link = link[: link.find("?")]
            # Update dictionary
            movie_dict = {"Index": self.item_index, "Name": name, "Link": link}
            links.append(movie_dict)
            print(f"Extracting links: {index}/{movie_count}", end="\r")
        print(f"\nFinish extracting from {url}")
        return links


def write(items: list[dict]):
    with open("./database/movie_links.csv", "a") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
        writer.writerows(items)


def main():
    with open("./database/movie_links.csv", "w") as writefile:
        writer = csv.DictWriter(writefile, fieldnames=FIELD_NAMES)
        writer.writeheader()

    grabber = ImdbLinkGrabber()
    # year_range = range(2024, 1910, -1)
    year_range = range(1912, 1910, -1)
    # Search strategy:
    # Release date: ___ - 10-2024, DESC
    # Rating: 1.0 - 10.0
    # Number of votes: >= 1000
    for year in year_range:
        search_range = f"{year}-01-01,{year}-12-31"
        min_vote = 1000
        print(f"Search range: {search_range}")
        url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={search_range}&user_rating=1,10&num_votes={min_vote},&sort=release_date,desc"
        items = grabber.grab_links(url)
        write(items)
    print("Done")


if __name__ == "__main__":
    main()
