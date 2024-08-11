import requests
import os
from bs4 import BeautifulSoup
from typing import List
import time
from pathlib import Path
from models.product import Product
from models.scrape_config import ScrapeConfig
import settings

class Scraper:

    def __init__(self, base_url: str, config: ScrapeConfig):
        self.base_url = base_url
        self.config = config
        self.session = requests.Session()

        if config.proxy:
            self.session.proxies = {'http': config.proxy, 'https': config.proxy}

    def scrape_page(self, page_num: int) -> List[Product]:
        url = f"{self.base_url}/page/{page_num}?a=1" if page_num > 1 else f"{self.base_url}?a=1"
        print (url)
        retries = self.config.max_fetch_retries
        while retries > 0:
            try:
                response = self.session.request("GET", url, timeout=10)
                response.raise_for_status()
                print(f'Starting scraping page {page_num}')
                return self.parse_products(response.text, page_num)
            except (requests.HTTPError, requests.ConnectionError):
                retries -= 1
                time.sleep(self.config.retry_delay_seconds)
                print ('Retrying Connection...')
        return []

    def parse_products(self, html: str, page_num: int) -> List[Product]:
        soup = BeautifulSoup(html, 'html.parser')
        products = []
        for product_tag in soup.select('.product'):
            pdt_thumbnail = product_tag.select_one('.attachment-woocommerce_thumbnail')
            title = pdt_thumbnail['title'] if pdt_thumbnail else ''
            pdt_amount = product_tag.find('span', class_='woocommerce-Price-amount')
            price = float(pdt_amount.get_text(strip=True).replace('₹', '')) if pdt_amount else 0.0
            pdt_img_url = product_tag.select_one('.attachment-woocommerce_thumbnail')
            image_url = pdt_img_url['src'] if pdt_img_url else ''
            # Download the image from its url and save it to a local directory
            image_file_path = self._download_and_save_image(image_url[0] if isinstance(image_url, List) else image_url, settings.DOWNLOAD_DIR)
            products.append(Product(product_title=title[0] if isinstance(title, List) else title, product_price=price, path_to_image=image_file_path))
        print (f'Done with {page_num}')
        return products

    def scrape(self) -> List[Product]:
        all_products = []
        for i in range(1, self.config.pages_limit + 1):
            products = self.scrape_page(i)
            if not products:
                break
            all_products.extend(products)
        return all_products
    
    def _download_and_save_image(self, image_url: str, save_dir_path: str) -> str:
        Path(save_dir_path).mkdir(parents=True, exist_ok=True)
        image_name = image_url.split('/')[-1]
        image_name = os.path.basename(image_url)
        save_full_path = os.path.join(save_dir_path, image_name)
    
        response = requests.get(image_url, stream=True)
        response.raise_for_status()

        # Write the image to the file in chunks to handle large files
        with open(save_full_path, 'wb') as file:
            for chunk in response.iter_content(1024):
                file.write(chunk)
    
        return os.path.abspath(os.path.join(save_dir_path, image_name))
