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
    # book = BookModel(keyword="파이썬", publisher="BJPublic", price=1200, image="me.png")
    # save 함수가 async 함수임 그렇기때문에 await 필요
    # print(await mongodb.engine.save(book))
    return templates.TemplateResponse(
        "./index.html", {"request": request, "title": "콜렉터스 북북이"}
    )


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    # 1. 쿼리에서 검색어 추출
    keyword = q
    # (예외처리)
    # - 검색어가 없다면 사용자에게 검색을 요구 return
    if not keyword:
        return templates.TemplateResponse(
            "./index.html", {"request": request, "title": "콜렉터스 북북이"}
        )
    # - 해당 검색어에 대한 수집된 데이터가 이미 DB에 존재한다면
    #   해당 데이터를 DB에서 조회하여 사용자에게 return

    if await mongodb.engine.find_one(BookModel, BookModel.keyword == keyword):
        books = await mongodb.engine.find(BookModel, BookModel.keyword == keyword)
        return templates.TemplateResponse(
            "./index.html",
            {
                "request": request,
                "title": "콜렉터스 북북이",
                "books": books,
            },
        )
    # 2. 데이터 수집기를 해당 검색어에 대해 데이터를 수집한다.
    scraper = NaverBookScraper()
    books = await scraper.search(keyword, 5)

    # 3. DB에 수집한 데이터를 저장한다.
    book_models = [
        BookModel(
            keyword=keyword,
            publisher=book["publisher"],
            price=book["price"],
            image=book["image"],
        )
        for book in books
    ]

    # mongoDB.engine.saveall(models) asyncio.gather()로 save
    await mongodb.engine.save_all(book_models)
    print(f"Save All! {keyword}")
    return templates.TemplateResponse(
        "./index.html",
        {
            "request": request,
            "title": "콜렉터스 북북이",
            "books": books,
        },
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
