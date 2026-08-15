from abc import ABC, abstractmethod


class Parser(ABC):
    TITLE: str = None
    PRODUCT_CODE: str = None
    REVIEWS : str = None

    @abstractmethod
    def get_element_text(self) -> str: ...

    @abstractmethod
    def _get_characteristic_element(self) -> str: ...

    @abstractmethod
    def _get_photos(self) -> list[str]: ...

    @abstractmethod
    def _get_prices(self) -> dict[str, str]: ...

    @abstractmethod
    def _get_characteristics(self) -> dict[str, str]: ...

    def get_data(self) -> dict:
        data = {
            "title": self.get_element_text(
                self.TITLE,
            ),
            "color": self._get_characteristic_element("Колір"),
            "storage": self._get_characteristic_element("Вбудована пам'ять"),
            "photos": self._get_photos(),
            "product_code": self.get_element_text(self.PRODUCT_CODE),
            "reviews": self.get_element_text(
                self.REVIEWS
            ),
            "screen_diagonal": self._get_characteristic_element("Діагональ екрану"),
            "display_resolution": self._get_characteristic_element(
                "Роздільна здатність екрану"
            ),
            "characteristics": self._get_characteristics(),
        }
        data.update(self._get_prices())
        return data
