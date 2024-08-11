import json
import redis
from typing import List
from models.product import Product

class CacheHandler:
    def __init__(self, redis_host: str):
        self.redis_client = redis.Redis.from_url(f'redis://{redis_host}:6379')

    def is_product_updated(self, product: Product) -> bool:
        cached_product = self.redis_client.get(product.product_title)
        print (f'GET {product.product_title}')
        if cached_product:
            de_product = Product(**json.loads((cached_product)))
            cached_price = de_product.product_price
            # scrapped product price is same as the cached price - no need for cache updation
            if cached_price == product.product_price:
                return False
        # scrapped product price is different - cache update required
        self.redis_client.set(product.product_title, json.dumps(product.__dict__))
        print (f'SET {product.product_title}')
        return True

    def filter_updated_products(self, products: List[Product]) -> List[Product]:
        return [product for product in products if self.is_product_updated(product)]

