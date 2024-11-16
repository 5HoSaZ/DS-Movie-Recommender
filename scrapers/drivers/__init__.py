from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions

import os
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
    def __init__(self):
        self.__api_key = self.__get_api_key()
        self.__header = {
            "accept": "application/json",
            "Authorization": f"Bearer {self.__api_key}",
        }

    def __get_api_key(self):
        api_path = "./scrapers/drivers/apikey/moviedb.txt"
        if not os.path.isfile(api_path):
            api_key = input("Input tmdb apikey: ")
            with open(api_path, "w") as file:
                file.write(api_key)
        with open(api_path, "r") as file:
            return file.readline()

    def get(self, url: str):
        response = requests.get(url, headers=self.__header)
        return json.loads(response.text)
