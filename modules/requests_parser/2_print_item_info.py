"""
Виводить інформацію про продукт за його посиланням. 
"""

from modules.load_django import *  # noqa: I001
from parser_app.services.product import ProductService  # type: ignore
from parser_app.types import ProductCreateData # type: ignore

from .constants import URL


def print_product(url: str):
    product = ProductService.get(url)
    if not product:
        print("Продукт не знайдено")
    print(ProductCreateData.from_model(product))


if __name__ == "__main__":
    print_product(URL)
