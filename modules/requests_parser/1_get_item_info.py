"""
Requests-based product parser.
Fetches product page using HTTP requests and extracts product information using BeautifulSoup.
Saves extracted data to Django database. Lightweight alternative to browser automation.
"""

import re  # noqa: I001

import requests
from bs4 import BeautifulSoup, Tag

from modules.load_django import *
from modules.parser import Parser
from parser_app.services.product import ProductService  # type: ignore
from .constants import URL


type SelectResult = Tag | None


class ItemFetcher:
    def __init__(self, url: str):
        self.url = url

    def fetch_html(self) -> str:
        self.response = requests.get(url=self.url)
        self.response.raise_for_status()
        return self.response.text


# python -m modules.requests_parser.1_get_item_info


class ItemParser(Parser):
    TITLE = ".main-title"
    REVIEWS = ".reviews-count span"
    PRODUCT_CODE = "#product_code"

    def __init__(self, html: str):
        self._html = html
        self.soup = BeautifulSoup(html, "html.parser")

    @staticmethod
    def _get_text(tag: SelectResult) -> str | None:
        if not tag:
            return
        return tag.get_text(strip=True)

    @property
    def characteristics(self) -> SelectResult:
        return self.soup.css.select_one(".br-pr-chr")

    def _get_characteristic_element(self, name: str):
        """Отримує характеристику товару по її назві"""
        characteristics = self.characteristics
        if not characteristics:
            return
        char_name = characteristics.find(string=name)
        if not char_name:
            return
        char_span = char_name.parent
        if not char_span:
            return
        char = char_span.find_next_sibling()
        return self._get_text(char)

    def _get_photos(self) -> list[str]:
        photos_div = self.soup.select_one(".product-block-bottom")
        if not photos_div:
            return []
        return [photo.get("src", "") for photo in photos_div.find_all("img")]

    def _get_characteristics(self) -> dict:
        _characteristics = self.soup.select(".br-pr-chr .br-pr-chr-item div div")
        characteristics = {}
        for char_item in _characteristics:
            char = char_item.find_all("span")
            if len(char) != 2:
                continue
            name, value = char
            characteristics[name.get_text(strip=True)] = re.sub(
                r"\s+", " ", value.get_text(strip=True)
            )
        return characteristics

    def get_element_text(self, selector: str) -> str | None:
        return self._get_text(self.soup.select_one(selector))

    def _get_prices(self):
        prices = {}
        current_price = self.get_element_text(".br-pr-np span")
        if not current_price:
            return prices
        def_price = self.get_element_text(".br-pr-op span")
        if not def_price:
            prices["price"] = current_price.replace(" ", "").replace(",", ".")
        else:
            prices["price"] = def_price.replace(" ", "").replace(",", ".")
            prices["sale_price"] = current_price.replace(" ", "").replace(",", ".")
        return prices


if __name__ == "__main__":
    fetcher = ItemFetcher(URL)
    item_scraper = ItemParser(fetcher.fetch_html())
    data = ProductService.build_create_data(data=item_scraper.get_data(), url=URL)
    print(data)
    ProductService.save(data)
