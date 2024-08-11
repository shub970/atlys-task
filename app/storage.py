from abc import ABC, abstractmethod
import json
from pathlib import Path
from typing import List, Mapping
from models.product import Product
from models.scrape_config import ScrapeConfig


class StorageHandler(ABC):
    @abstractmethod
    def save(self, products: List[Product]):
        pass

    @abstractmethod
    def load(self) -> List[Product]:
        pass


# using Factory pattern here for extendibility
def StorageHandlerFactory(storage_type: str, opts: Mapping[str, str]):
    stores = {
        "local": LocalStorage
    }
    return stores[storage_type](opts)

# Implementation for local storage
class LocalStorage(StorageHandler):

    def __init__(self, opts: Mapping[str, str]) -> None:
        super().__init__()
        self.storage_file = opts['storage_file']

    def save(self, products: List[Product]):
        existing_data = self.load()
        existing_data.extend(products)
        with open(self.storage_file, 'w') as file:
            json.dump([product.model_dump() for product in existing_data], file, indent=4)

    def load(self) -> List[Product]:
        if Path(self.storage_file).exists():
            with open(self.storage_file, 'r') as file:
                return [Product(**item) for item in json.load(file)]
        return []
