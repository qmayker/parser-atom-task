from dataclasses import dataclass, field, fields


@dataclass
class ProductCreateData:
    title: str
    url: str
    color: str | None = None
    storage: str | None = None
    product_code: str | None = None
    reviews: int | None = None
    screen_diagonal: str | None = None
    display_resolution: str | None = None
    photos: list[str] = field(default_factory=list)
    characteristics: dict = field(default_factory=dict)

    @classmethod
    def from_model(cls, product):
        data = {}

        for data_field in fields(cls):
            data[data_field.name] = getattr(product, data_field.name)

        return cls(**data)
