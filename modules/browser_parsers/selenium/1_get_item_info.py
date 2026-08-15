"""
Visits url, opens first item found and returns info about it
"""

import random  # noqa: I001
import re
import time
from typing import ClassVar


from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_parsers import constants
from modules.load_django import *
from modules.parser import Parser
from parser_app.services.product import ProductService  # type: ignore

# python -m modules.browser_parsers.selenium.1_get_item_info


class SeleniumDriver:
    def __init__(self):
        self.driver = webdriver.Chrome(options=self.options)

    @property
    def options(self) -> webdriver.ChromeOptions:
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=uk-UA")

        return options


class Browser:
    SEARCH_CLASSES: ClassVar = ["header-bottom", "header-top-in"]
    SEARCH_INPUT_XPATH = "//div[@class='{}']//input[@class='quick-search-input']"
    LISTING_XPATH = "//div[@class='view-grid tab-pane row br-row br-flex active']"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @property
    def search_xpath(self):
        return self.SEARCH_INPUT_XPATH.format(self.search_class)

    def open_url(self, url: str):
        self.url = url
        self.driver.get(url)

    def _type_text(self, input_element: WebElement, text: str):
        try:
            input_element.send_keys(text, Keys.ENTER)
        except ElementNotInteractableException:
            return self._type_text(self.get_input_element(self.search_xpath), text=text)
        time.sleep(random.uniform(0.03, 0.12))

    def get_input_element(self, xpath: str):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element

    def _search(self, text: str) -> bool:
        input_element = self.get_input_element(self.search_xpath)
        if not (input_element.is_enabled() and input_element.is_displayed()):
            return False
        try:
            self._type_text(input_element, text)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//div[@class='search-result']")
                )
            )
            return True
        except ElementNotInteractableException:
            return False
        except NoSuchElementException:
            return False

    def search(self, text: str) -> bool:
        for search_class in self.SEARCH_CLASSES:
            self.search_class = search_class
            succeeded = self._search(text)
            if succeeded:
                break
        return succeeded

    def get_listing(self) -> list[WebElement]:
        listing_div = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, self.LISTING_XPATH))
        )
        listing = listing_div.find_elements(By.XPATH, "./*")
        return listing

    def get_item_page(self, item: WebElement) -> bool:
        try:
            item_name = item.find_element(
                By.XPATH, ".//div[@class='description-wrapper']//a"
            )
        except NoSuchElementException:
            return False
        item_url = item_name.get_attribute("href")
        if not item_url:
            return False
        self.open_url(item_url)
        return True

    def stop(self):
        self.driver.stop_client()


class ItemParser(Parser):
    TITLE = "//h1[@class='desktop-only-title']"
    PRODUCT_CODE = "//span[@class='br-pr-code-val']"
    REVIEWS = "//a[@class='scroll-to-element reviews-count']//span"

    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    @property
    def _characteristics(self) -> WebElement:
        return self.driver.find_element(By.XPATH, "//div[@class='br-pr-chr']")

    def get_element_text(self, xpath: str) -> str | None:
        try:
            element = self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None
        return element.get_attribute("textContent").strip()

    def _get_characteristic_element(self, name: str):
        char = self._characteristics.find_element(
            By.XPATH, f'//*[contains(text(), "{name}")]'
        )
        char_value = char.find_element(By.XPATH, "..//a")
        return char_value.get_attribute("textContent").strip()

    def _get_photos(self) -> list[str]:
        images = self.driver.find_elements(
            By.XPATH,
            "//div[@class='product-block-bottom']//div[@class='slick-track']//img",
        )
        return [image.get_attribute("src") for image in images]

    def _get_prices(self) -> dict:
        prices = {}
        try:
            current_price = self.get_element_text("//div[@class='br-pr-np']//span")
        except NoSuchElementException:
            return prices
        try:
            def_price = self.get_element_text("//div[@class='br-pr-op']//span")
            prices["price"] = def_price.replace(" ", "").replace(",", ".")
            prices["sale_price"] = current_price.replace(" ", "").replace(",", ".")
        except NoSuchElementException:
            prices["price"] = current_price.replace(" ", "").replace(",", ".")
        return prices

    def _get_characteristics(self) -> dict:
        characteristics = {}
        try:
            _characteristics = self.driver.find_elements(
                By.XPATH, "//div[@class='br-pr-chr']//div//div//div"
            )
        except NoSuchElementException:
            return {}
        for characteristic in _characteristics:
            try:
                res = characteristic.find_elements(By.XPATH, ".//span")
            except NoSuchElementException:
                continue
            if len(res) != 2:
                continue
            key, value = res
            characteristics[key.get_attribute("textContent").strip()] = re.sub(
                r"\s+", " ", value.get_attribute("textContent").strip()
            )
        return characteristics


def get_first_element_info():
    driver = SeleniumDriver()
    browser = Browser(driver.driver)
    browser.open_url(constants.URL)
    browser.search(constants.SEARCH_TEXT)
    listing = browser.get_listing()
    if not listing:
        return
    if not browser.get_item_page(listing[0]):
        return
    parser = ItemParser(driver.driver)
    data = ProductService.build_create_data(parser.get_data(), browser.url)
    print(data)
    ProductService.save(data)
    browser.stop()


if __name__ == "__main__":
    get_first_element_info()
