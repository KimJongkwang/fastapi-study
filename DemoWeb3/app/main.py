from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.scripts.book_scraper import BookScraper
from app.models import mongodb
from app.models.books import BookModel


BASE_DIR = Path(__file__).resolve().parent
app = FastAPI()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, q: str):
    if not q:
        return templates.TemplateResponse("index.html", {"request": request})
    if await mongodb.engine.find_one(BookModel, BookModel.keyword == q):
        books = await mongodb.engine.find(BookModel, BookModel.keyword == q)
        print("DB에서 가져왔습니다.")
        return templates.TemplateResponse(
            "index.html", {"request": request, "books": books}
        )

    scraper = BookScraper()
    print("Data를 수집 중 입니다.")
    books = await scraper.search(q, 5)
    book_models = [
        BookModel(
            keyword=q,
            title=book["title"],
            publisher=book["publisher"],
            price=book["price"],
            image=book["image"],
        )
        for book in books
    ]
    await mongodb.engine.save_all(book_models)
    return templates.TemplateResponse(
        "index.html", {"request": request, "books": books}
    )


@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    mongodb.close()
