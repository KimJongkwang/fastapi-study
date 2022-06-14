from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/search", response_class=HTMLResponse)
async def search_book(request: Request, q: str):
    """
    mongodb --> mysql 이관해보자

    Args:
        request (Request): _description_
        q (str): _description_
    """
    # if not q:
    #     return templates.TemplateResponse("index.html", {"request": request})
    # if await mongodb.engine.find_one(BookModel, BookModel.keyword == q):
    #     books = await mongodb.engine.find(BookModel, BookModel.keyword == q)
    #     print("DB에서 가져왔습니다.")
    #     return templates.TemplateResponse(
    #         "index.html", {"request": request, "books": books}
    #     )

    # scraper = BookScraper()
    # print("Data를 수집 중 입니다.")
    # books = await scraper.search(q, 5)
    # book_models = [
    #     BookModel(
    #         keyword=q,
    #         title=book["title"],
    #         publisher=book["publisher"],
    #         price=book["price"],
    #         image=book["image"],
    #     )
    #     for book in books
    # ]
    # await mongodb.engine.save_all(book_models)
    # return templates.TemplateResponse(
        # "index.html", {"request": request, "books": books}
    # )
    ...
