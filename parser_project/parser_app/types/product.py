from dataclasses import dataclass, field


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
