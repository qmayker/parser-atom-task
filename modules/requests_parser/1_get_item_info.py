"""
Збирає інформацію про товар, та зберігає до бд
"""

import re  # noqa: I001

import requests
from bs4 import BeautifulSoup, Tag

from modules.load_django import *
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


class ItemScraper:
    def __init__(self, html: str):
        self._html = html
        self.soup = BeautifulSoup(html, "html.parser")

    @staticmethod
    def _get_text(tag: SelectResult) -> str:
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
        return char

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

    def get_data(self) -> dict:
        tags = {
            "title": self.soup.select_one(".main-title"),
            "color": self._get_characteristic_element("Колір"),
            "storage": self._get_characteristic_element("Вбудована пам'ять"),
            "product_code": self.soup.select_one("#product_code"),
            "reviews": self.soup.select_one(".reviews-count span"),
            "screen_diagonal": self._get_characteristic_element("Діагональ екрану"),
            "display_resolution": self._get_characteristic_element(
                "Роздільна здатність екрану"
            ),
        }
        product_info = {}
        for key, value in tags.items():
            product_info[key] = self._get_text(value)
        additional_info = {
            "photos": self._get_photos(),
            "characteristics": self._get_characteristics(),
        }
        product_info.update(additional_info)
        return product_info


if __name__ == "__main__":
    fetcher = ItemFetcher(URL)
    item_scraper = ItemScraper(fetcher.fetch_html())
    data = ProductService.build_create_data(data=item_scraper.get_data(), url=URL)
    ProductService.save(data)
