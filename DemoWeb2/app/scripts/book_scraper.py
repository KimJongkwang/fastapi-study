import aiohttp
import asyncio
from pathlib import Path

from app.config.config import get_secrets

BASE_DIR = Path(__file__).resolve().parent


class BookScraper:
    async def main(
        self,
        keyword,
    ):

        URL = "https://openapi.naver.com/v1/search/image?query="

        async with aiohttp.ClientSession() as session:
            async with session.get(f"{URL}" + keyword) as response:
                pass

        pass
