"""
Playwright-based product parser.
Visits URL, searches for a product, opens the first result, and extracts all product information.
Uses Playwright for headless/headed browser automation with better performance and stability.
"""

import re

from playwright.sync_api import Browser, Locator, TimeoutError, sync_playwright

from modules.browser_parsers import constants, services


class PlaywrightService:
    def __init__(self):
        self.playwright = self.start()
        self.browser = self.playwright.chromium.launch(**self.browser_options)

    @property
    def browser_options(self):
        return {"headless": False}

    def start(self):
        return sync_playwright().start()

    def stop(self):
        self.playwright.stop()

    def close(self):
        self.browser.close()

    def end(self):
        self.close()
        self.stop()


class PageService(services.PageService):
    def __init__(self, browser: Browser):
        self.browser = browser
        self.page = self.browser.new_page()

    def open_url(self, url: str):
        self.url = url
        self.page.goto(url)

    def wait_for(self, xpath: str) -> Locator:
        locator = self.page.locator(f"xpath={xpath}")
        locator.wait_for(timeout=10_000, state="attached")
        return locator

    def find_elements(self, xpath: str):
        return self.page.locator(f"xpath={xpath}").all()

    def find_element(self, xpath: str):
        return self.page.locator(f"xpath={xpath}").first


class SearchService(services.BaseSearchService[PageService]):
    def _type_text(self, locator: Locator, text: str) -> bool:
        try:
            locator.fill(text)
            locator.press("Enter")
        except TimeoutError:
            return False
        self.page.sleep_random()
        return True

    def _search(self, text):
        try:
            locator = self.page.wait_for(self.search_xpath)
        except TimeoutError:
            return False
        if not (locator.is_visible() and locator.is_enabled()):
            return False
        return self._type_text(locator, text)


class ItemsService(services.ItemsService[PageService]):
    def get_listing(self) -> list[Locator]:
        listing_div = self.page.wait_for(self.LISTING_XPATH)
        listing = listing_div.locator("xpath=./*").all()
        return listing

    def open_item(self, item: Locator):
        item_name = item.locator(f"xpath={self.ITEM_DESCRIPTION}")
        try:
            item_url = item_name.get_attribute("href", timeout=10000)
            if not item_url:
                return False
        except TimeoutError:
            return False

        self.page.open_url(item_url)
        return True


class ItemParser(services.ItemParser[PageService]):
    def get_element_text(self, xpath) -> str | None:
        try:
            locator = self.page.find_element(xpath)
            return locator.text_content(timeout=10000).strip()
        except TimeoutError:
            return None

    def _get_characteristic_element(self, name):
        characteristic: Locator = self._get_characteristic(name)
        char_value = characteristic.locator("xpath=..//a")
        return char_value.text_content(timeout=10000).strip()

    def _get_photos(self):
        return [image.get_attribute("src") for image in self._photos]

    def _get_prices(self) -> dict:
        prices = {}
        try:
            current_price = self.get_element_text("//div[@class='br-pr-np']//span")
        except TimeoutError:
            return prices
        try:
            def_price = self.get_element_text("//div[@class='br-pr-op']//span")
            prices["price"] = def_price.replace(" ", "").replace(",", ".")
            prices["sale_price"] = current_price.replace(" ", "").replace(",", ".")
        except TimeoutError:
            prices["price"] = current_price.replace(" ", "").replace(",", ".")
        return prices

    def _get_characteristics(self) -> dict:
        characteristics = {}
        try:
            _characteristics = self.page.find_elements(
                "//div[@class='br-pr-chr']//div//div//div"
            )
        except TimeoutError:
            return {}
        for characteristic in _characteristics:
            try:
                res = characteristic.locator("xpath=.//span").all()
            except TimeoutError:
                continue
            if len(res) != 2:
                continue
            key = res[0].text_content(timeout=10000).strip()
            value = res[1].text_content(timeout=10000).strip()
            characteristics[key] = re.sub(r"\s+", " ", value)
        return characteristics


def get_first_element_info(
    page: PageService,
    search_service: SearchService,
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


if __name__ == "__main__":
    playwright = PlaywrightService()
    page = PageService(playwright.browser)
    search_service = SearchService(page)
    items_service = ItemsService(page)
    item_parser = ItemParser(page)
    data = services.get_first_element_info(
        page, search_service, items_service, item_parser
    )
    print(data)
    playwright.end()
