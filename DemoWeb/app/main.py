from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.models import mongodb
from app.models.book import BookModel
from app.book_scraper import NaverBookScraper

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI()

templates = Jinja2Templates(directory=BASE_DIR / "templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    book = BookModel(keyword="파이썬", publisher="BJPublic", price=1200, image="me.png")
    # save 함수가 async 함수임 그렇기때문에 await 필요
    print(await mongodb.engine.save(book))
    return templates.TemplateResponse(
        "./index.html", {"request": request, "title": "콜렉터 북북이"}
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    scraper = NaverBookScraper()
    data = await scraper.search(q, 5)
    return templates.TemplateResponse(
        "./index.html", {"request": request, "keyword": q, "data": data}
    )


# fastapi에 이벤트 등록: 서버가 구동할 때 실행하는 코드
@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    """서버가 의도하지 않은 상태로 종료될 경우 백업 마이그레이션 코드작성 또는 로깅 작성할 수 도 있음"""
    mongodb.close()
    print("bye server!!")
