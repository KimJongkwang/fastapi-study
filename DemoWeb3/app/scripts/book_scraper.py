import re
import asyncio
import aiohttp
from pathlib import Path

from app.config.config import get_secrets

BASE_DIR = Path(__file__).resolve().parent


class BookScraper:

    URL = "https://openapi.naver.com/v1/search/book?query="
    API_KEY = {
        "X-Naver-Client-Id": get_secrets("NAVER_API_ID"),
        "X-Naver-Client-Secret": get_secrets("NAVER_API_SECRET"),
    }

    @staticmethod
    async def fetch(session, url):
        async with session.get(url, headers=BookScraper.API_KEY) as response:
            if response.status == 200:
                result = await response.json()
                data = result["items"]
                return data
            else:
                print(f"{response.status} Error")

    async def search(self, keyword, total_page):
        urls = [
            self.URL + f"{keyword}&display=10&start={i*10+1}" for i in range(total_page)
        ]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[BookScraper.fetch(session, url) for url in urls]
            )
            result = []
            for data in all_data:
                if data is not None:
                    for book in data:
                        book["title"] = re.sub(
                            "(<([^>]+)>)", " ", book["title"]
                        ).replace("  ", " ")
                        book["publisher"] = re.sub(
                            "(<([^>]+)>)", " ", book["publisher"]
                        ).replace("  ", " ")
                        result.append(book)
        return result
