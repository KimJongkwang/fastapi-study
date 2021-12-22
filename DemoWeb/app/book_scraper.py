import asyncio
import aiohttp
from app.config import get_secret


class NaverBookScraper:

    URL = "https://openapi.naver.com/v1/search/image"
    HEADERS = {
        "X-Naver-Client-Id": get_secret("NAVER_API_ID"),
        "X-Naver-Client-Secret": get_secret("NAVER_API_SECRET"),
    }

    @staticmethod
    async def fetch(session, url):
        async with session.get(url, headers=NaverBookScraper.HEADERS) as response:
            if response.status == 200:
                result = await response.json()
                return result["items"]

    def unit_url(self, keyword, start):
        return f"{self.URL}?query={keyword}&display=10&start={start}"

    async def search(self, keyword, total_page):
        urls = [self.unit_url(keyword, (1 + i * 10)) for i in range(total_page)]
        async with aiohttp.ClientSession() as session:
            all_data = await asyncio.gather(
                *[NaverBookScraper.fetch(session, url) for url in urls]
            )
            result = []
            for data in all_data:
                if data is not None:
                    for book in data:
                        result.append(book)
            # print(result)
        return result

    def run(self, keyword, total_page):
        return asyncio.run(self.search(keyword, total_page))
