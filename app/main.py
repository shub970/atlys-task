from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import APIKeyHeader
from scraper import ScrapeConfig, Scraper
from models.scrape_config import ScrapeConfig
from storage import StorageHandlerFactory
from notification import NotificationHandlerFactory
from cache import CacheHandler
import settings

app = FastAPI()

api_token_header = APIKeyHeader(name="X-AUTH-TOKEN")

def authenticate(auth_token: str = Security(api_token_header)):
    if auth_token != settings.AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Unauthorized")
    return True

@app.post("/scrape/")
async def scrape(config: ScrapeConfig, token: str = Depends(authenticate)):
    scraper = Scraper(base_url=settings.BASE_URL, config=config) 
    products = scraper.scrape()

    # Handle Storage
    storage_handler = StorageHandlerFactory("local", {'storage_file': settings.STORAGE_FILE})

    cache = CacheHandler(settings.REDIS_HOST)
    updated_products = cache.filter_updated_products(products)
    storage_handler.save(updated_products)
    
    # Handle Notification
    notif_message = f'{len(products)} products were scraped and updated in DB during the current session'
    notification_handler = NotificationHandlerFactory(medium="console")
    notification_handler.notify(notif_message)

    return {"message": f"Scraped {len(products)} products and updated {len(updated_products)} products in the storage."}