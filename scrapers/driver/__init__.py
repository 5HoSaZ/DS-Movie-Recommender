from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options as FirefoxOptions


class FireFoxDriver(webdriver.Firefox):
    def __init__(self):
        options = FirefoxOptions()
        options.binary_location = "C:/Program Files/Mozilla Firefox/firefox.exe"
        options.set_preference("permissions.default.image", 2)
        service = Service(executable_path="./drivers/firefox/geckodriver.exe")
        super().__init__(options, service, True)


if __name__ == "__main__":
    a = FireFoxDriver()
