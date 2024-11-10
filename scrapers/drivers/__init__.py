from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions
import os


class FireFoxDriver(webdriver.Firefox):
    EXE_PATH = "./scrapers/drivers/geckodriver.exe"

    def __init__(self):
        options = FirefoxOptions()
        options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
        options.set_preference("permissions.default.image", 2)
        service = Service(executable_path=self.EXE_PATH)
        super().__init__(options, service, True)


if __name__ == "__main__":
    a = FireFoxDriver()
