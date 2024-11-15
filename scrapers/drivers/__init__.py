from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import requests
import json


class FireFoxDriver(webdriver.Firefox):
    EXE_PATH = "./scrapers/drivers/geckodriver.exe"

    def __init__(self):
        options = FirefoxOptions()
        options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
        options.set_preference("permissions.default.image", 2)
        service = Service(executable_path=self.EXE_PATH)
        super().__init__(options, service, True)


class Requester:
    def __init__(self, api_key: str):
        self.header = {
            "accept": "application/json",
            "Authorization": f"Bearer {api_key}",
        }

    def get(self, url: str):
        response = requests.get(url, headers=self.header)
        return json.loads(response.text)


if __name__ == "__main__":
    api_key = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiI2YWQ5YjkzZjNjMjA4NDE3MTM4YjU4MWViM2RhYmZmNCIsIm5iZiI6MTczMTM3OTI5NS41MjYwOTksInN1YiI6IjY3MzJiZTkyNTc1ZDA2OWQzOWZjNzZmYyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.htOfonsD20xG8V1pl0VU9fGQ2mHcpG4-lyiuj2BQqzo"
    a = Requester(api_key)
    res = a.get("https://api.themoviedb.org/3/movie/278155?language=en-US")
    print(res)
