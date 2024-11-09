from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import time
from datetime import datetime
import csv
import pandas as pd
import os

options = FirefoxOptions()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
service = Service(executable_path="./drivers/firefox/geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)


# Data wrapper
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
def get_countries_of_origin(element):
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


def get_entry(url, name=""):
    entry_dict = {"ImdbID": get_id(url), "Name": name}
    driver.get(url)
    elements = driver.find_elements(By.TAG_NAME, "section")
    for e in elements:
        if attr := e.get_attribute("data-testid"):
            match attr:
                case "atf-wrapper-bg":
                    entry_dict["Plot"] = get_plot(e)
                    entry_dict["Rating"] = get_imdb_rating(e)
                    entry_dict["Genres"] = get_genres(e)
                    entry_dict["Runtime"] = get_run_time(e)
                case "Details":
                    entry_dict["ReleaseDate"] = get_release_date(e)
                    entry_dict["OriginCountries"] = get_countries_of_origin(e)
                    entry_dict["Languages"] = get_languages(e)
    time.sleep(1)
    return entry_dict


def main():
    fieldnames = [
        "ImdbID",
        "Name",
        "Runtime",
        "ReleaseDate",
        "OriginCountries",
        "Languages",
        "Genres",
        "Rating",
        "Plot",
    ]
    if not os.path.isfile("./database/movie_entries.csv"):
        with open("./database/movie_entries.csv", "w") as writefile:
            writer = csv.DictWriter(writefile, fieldnames=fieldnames)
            writer.writeheader()

    to_process_count = len(
        pd.read_csv("./database/movie_links.csv", encoding="latin-1")
    )
    processed = pd.read_csv("./database/movie_entries.csv", encoding="latin-1")
    processed_id = set(processed["ImdbID"].values)
    with open("./database/movie_links.csv", "r") as readfile:
        reader = csv.DictReader(readfile)

        for i, row in enumerate(reader):
            name, url = row["Name"], row["Link"]
            print(f"({i + 1}/{to_process_count}) Getting data from {url}", end="\r")
            if get_id(url) in processed_id:
                continue
            with open(
                "./database/movie_entries.csv", "a", encoding="utf-8"
            ) as writefile:
                writer = csv.DictWriter(writefile, fieldnames=fieldnames)
                writer.writerow(get_entry(url, name))
            print("\nDone")


def test():
    url = "https://www.imdb.com/title/tt29268110/"
    entry_dict = {}
    driver.get(url)
    elements = driver.find_elements(By.TAG_NAME, "section")
    for e in elements:
        if attr := e.get_attribute("data-testid"):
            match attr:
                case "atf-wrapper-bg":
                    pass
                    # entry_dict["Plot"] = get_plot(e)
                    # entry_dict["Rating"] = get_imdb_rating(e)
                    # entry_dict["Genres"] = get_genres(e)
                    # entry_dict["Runtime"] = get_run_time(e)
                case "Details":
                    # entry_dict["ReleaseDate"] = get_release_date(e)
                    # entry_dict["OriginCountry"] = get_countries_of_origin(e)
                    entry_dict["Language"] = get_languages(e)
    time.sleep(1)
    print(entry_dict)


if __name__ == "__main__":
    main()
    # test()
