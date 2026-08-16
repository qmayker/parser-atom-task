import random
import time
from abc import ABC, abstractmethod

from modules.browser_parsers import constants
from modules.parser import Parser


class PageService(ABC):
    @abstractmethod
    def open_url(self, url: str): ...

    def sleep_random(self):
        time.sleep(random.uniform(0.03, 0.12))

    def sleep(self, seconds: int):
        time.sleep(seconds)

    @abstractmethod
    def wait_for(self, xpath: str): ...

    @abstractmethod
    def find_elements(self, xpath: str): ...


class BaseSearchService[P](ABC):
    SEARCH_CLASSES = constants.SEARCH_CLASSES
    SEARCH_INPUT_XPATH = constants.SEARCH_INPUT_XPATH

    def __init__(self, page: P):
        self.page = page

    @abstractmethod
    def _search(self, text: str) -> bool:
        pass

    @property
    def search_xpath(self):
        return self.SEARCH_INPUT_XPATH.format(self.search_class)

    def search(self, text: str) -> bool:
        for search_class in self.SEARCH_CLASSES:
            self.search_class = search_class
            succeeded = self._search(text)
            if succeeded:
                break
        return succeeded


class ItemsService[P](ABC):
    LISTING_XPATH = constants.LISTING_XPATH
    ITEM_DESCRIPTION = constants.ITEM_DESCRIPTION

    def __init__(self, page: P):
        self.page = page

    @abstractmethod
    def get_listing(self) -> list: ...

    @abstractmethod
    def open_item(self, item) -> bool: ...


class ItemParser[P](Parser, ABC):
    TITLE = constants.TITLE
    PRODUCT_CODE = constants.PRODUCT_CODE
    REVIEWS = constants.REVIEWS

    def __init__(self, page: P):
        self.page = page

    def _get_characteristic(self, name: str):
        return self.page.find_element(
            f'//div[@class="br-pr-chr"]//*[contains(text(), "{name}")]'
        )

    @property
    def _photos(self):
        return self.page.find_elements(
            "//div[@class='product-block-bottom']//div[@class='slick-track']//img",
        )


def get_first_element_info(
    page: PageService,
    search_service: BaseSearchService,
    items_service: ItemsService,
    item_parser: ItemParser,
):
    page.open_url(constants.URL)
    if not search_service.search(constants.SEARCH_TEXT):
        return None
    listing = items_service.get_listing()
    if not listing:
        return None
    if not items_service.open_item(listing[0]):
        return None

    return item_parser.get_data()