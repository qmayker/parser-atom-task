"""
Business logic for product operations.
Handles saving and retrieving product data from the database.
"""

from dataclasses import asdict

from parser_app.choices import Parsers
from parser_app.models import Product
from parser_app.types import ProductCreateData


class ProductService:
    @staticmethod
    def save(product_data: ProductCreateData) -> Product:
        data = asdict(product_data)
        product, _ = Product.objects.update_or_create(
            url=data.pop("url"), parser=data.pop("parser"), defaults=data
        )
        return product

    @staticmethod
    def build_create_data(data: dict, url: str, parser: Parsers) -> ProductCreateData:
        return ProductCreateData(url=url, parser=parser, **data)
