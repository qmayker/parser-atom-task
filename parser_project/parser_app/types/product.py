from dataclasses import dataclass, field, fields


@dataclass
class ProductCreateData:
    url: str
    title: str
    color: str | None = None
    storage: str | None = None
    product_code: str | None = None
    reviews: int | None = None
    screen_diagonal: str | None = None
    display_resolution: str | None = None
    photos: list[str] = field(default_factory=list)
    characteristics: dict = field(default_factory=dict)
    price: float | None = None
    sale_price: float | None = None

    @classmethod
    def from_model(cls, product):
        data = {}

        for data_field in fields(cls):
            data[data_field.name] = getattr(product, data_field.name)

        return cls(**data)
