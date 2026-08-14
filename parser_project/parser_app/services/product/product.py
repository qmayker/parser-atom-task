from dataclasses import asdict

from parser_app.models import Product
from parser_app.types import ProductCreateData


class ProductService:
    @staticmethod
    def save(product_data: ProductCreateData):
        data = asdict(product_data)
        product, _ = Product.objects.update_or_create(
            url=data.pop("url"), defaults=data
        )
        return product

    @staticmethod
    def build_create_data(data: dict, url: str):
        return ProductCreateData(url=url, **data)
