from pydantic import BaseModel, Field


class ScrapeConfig(BaseModel):
    pages_limit: int = Field(default=5, ge=1)
    proxy: str = Field(default=None, pattern=r'^http://')
    retry_delay_seconds: int = Field(default=5, ge=1)
    max_fetch_retries: int = Field(default=3, ge=1)