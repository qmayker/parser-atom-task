"""
Selenium-based product parser.
Visits URL, searches for a product, opens the first result, and extracts all product information.
Saves extracted data to Django database. Uses Selenium WebDriver for browser automation.
"""

from modules.load_django import *  # noqa: I001

import re

from parser_app.services.product import ProductService  # type: ignore
from selenium import webdriver
from selenium.common.exceptions import (
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from modules.browser_parsers import services

# python -m modules.browser_parsers.selenium.1_get_item_info


class SeleniumService:
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

    def stop(self):
        self.driver.stop_client()


class PageService(services.PageService):
    def __init__(self, driver: webdriver.Chrome):
        self.driver = driver

    def open_url(self, url: str):
        self.url = url
        self.driver.get(url)

    def wait_for(self, xpath: str):
        element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element

    def find_element(self, xpath: str):
        return self.driver.find_element(By.XPATH, xpath)

    def find_elements(self, xpath: str):
        return self.driver.find_elements(By.XPATH, xpath)


class SearchService(services.BaseSearchService[PageService]):
    def type_text(self, input_element: WebElement, text: str):
        try:
            input_element.send_keys(text, Keys.ENTER)
        except ElementNotInteractableException:
            return self.type_text(self.page.wait_for(self.search_xpath), text=text)
        self.page.sleep_random()

    def _search(self, text: str) -> bool:
        try:
            input_element = self.page.wait_for(self.search_xpath)
        except TimeoutException:
            return False
        if not (input_element.is_enabled() and input_element.is_displayed()):
            return False
        try:
            self.type_text(input_element, text)
            self.page.wait_for("//div[@class='search-result']")
            return True
        except ElementNotInteractableException:
            pass
        except NoSuchElementException:
            pass
        return False


class ItemsService(services.ItemsService):
    def get_listing(self) -> list[WebElement]:
        listing_div = self.page.wait_for(self.LISTING_XPATH)
        listing = listing_div.find_elements(By.XPATH, "./*")
        return listing

    def open_item(self, item: WebElement) -> bool:
        try:
            item_name = item.find_element(By.XPATH, self.ITEM_DESCRIPTION)
        except NoSuchElementException:
            return False
        item_url = item_name.get_attribute("href")
        if not item_url:
            return False
        self.page.open_url(item_url)
        return True


class ItemParser(services.ItemParser[PageService]):
    def get_element_text(self, xpath: str) -> str | None:
        try:
            element = self.page.find_element(xpath)
        except NoSuchElementException:
            return None
        return element.get_attribute("textContent").strip()

    def _get_characteristic_element(self, name: str):
        char_value = self._get_characteristic(name).find_element(By.XPATH, "..//a")
        return char_value.get_attribute("textContent").strip()

    def _get_photos(self) -> list[str]:
        return [image.get_attribute("src") for image in self._photos]

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
            _characteristics = self.page.find_elements(
                "//div[@class='br-pr-chr']//div//div//div"
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


if __name__ == "__main__":
    service = SeleniumService()
    page = PageService(service.driver)
    search_service = SearchService(page)
    items_service = ItemsService(page)
    item_parser = ItemParser(page)

    data = services.get_first_element_info(
        page, search_service, items_service, item_parser
    )
    print(data)
    if data:
        data = ProductService.build_create_data(data, page.url)
        ProductService.save(data)

    service.stop()
