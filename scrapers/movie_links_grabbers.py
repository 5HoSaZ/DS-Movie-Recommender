from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
import time
import math
import pandas as pd

options = FirefoxOptions()
options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
service = Service(executable_path="./drivers/firefox/geckodriver.exe")
driver = webdriver.Firefox(service=service, options=options)

url = "https://www.imdb.com/search/title/?title_type=feature&release_date=,2024-10-31&user_rating=1,10&num_votes=1000,&sort=release_date,desc"
movie_links_data = "database/movie_links.csv"


# Get the total of movie found
def get_movie_count() -> int:
    count_field = driver.find_element(By.CLASS_NAME, "sc-13add9d7-3.fwjHEn")
    count = int(count_field.text.split(" ")[-1].replace(",", ""))
    return count


# Action perform to load more movies on browser
def get_50_more() -> bool:
    driver.execute_script(
        """
        var scrollingElement = (document.scrollingElement || document.body);
        scrollingElement.scrollTop = scrollingElement.scrollHeight;
        """
    )
    time.sleep(1)
    try:
        next_50_button = driver.find_element(By.CLASS_NAME, "ipc-see-more__text")
        next_50_button.click()
    except Exception:
        return False
    return True


def main():
    # Connect to url
    driver.get(url)
    movie_count = min(get_movie_count(), 4000)
    print(f"Scraper found {movie_count} movies.")
    # Loading movies
    for i in range(load_count := (math.ceil(movie_count / 50) - 1)):
        print(f"Loading items: {i + 1}/{load_count}", end="\r")
        success = False
        while not success:
            success = get_50_more()
            time.sleep(5)
    print("\nLoading complete")
    # Find all movies
    movie_dict = {"Index": [], "Name": [], "Link": []}
    for item in driver.find_elements(By.CLASS_NAME, "ipc-title-link-wrapper"):
        # Get index and name
        index, name = item.text.split(". ", maxsplit=1)
        # Get movie link
        link = item.get_attribute("href")
        link = link[: link.find("?")]
        # Update dictionary
        movie_dict["Index"].append(index)
        movie_dict["Name"].append(name)
        movie_dict["Link"].append(link)
        print(f"Extracting links: {index}/{movie_count}", end="\r")
    # Save to csv
    print(f"\nSaving to {movie_links_data}")
    pd.DataFrame(movie_dict).to_csv(movie_links_data, index=False)
    # Quit browser
    driver.quit()


if __name__ == "__main__":
    main()
