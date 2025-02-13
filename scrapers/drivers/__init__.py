from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import json
import requests


class FireFoxDriver(webdriver.Firefox):
    EXE_PATH = "./scrapers/drivers/geckodriver.exe"

    def __init__(self):
        options = FirefoxOptions()
        options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
        options.set_preference("permissions.default.image", 2)
        service = Service(executable_path=self.EXE_PATH)
        super().__init__(options, service, True)


class Requester:
    def __init__(self, api_key: str = None):
        if api_key is None:
            self.__api_key = input("Input tmdb apikey: ")
        else:
            self.__api_key = api_key
        self.__header = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.__api_key}",
        }

    def get(self, url: str, timeout: int = None):
        response = requests.get(url, headers=self.__header, timeout=timeout)
        return json.loads(response.text)
