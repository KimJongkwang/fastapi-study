from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path

from app.models import mongodb

# from app.models.books import BookModel

BASE_DIR = Path(__file__).resolve().parent


app = FastAPI()

templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search", response_class=HTMLResponse)
async def read_item(request: Request, q: str):
    # bookdata = BookModel(
    #     keyword="파이썬", publisher="BJpublic", price=1200, image="me.png"
    # )
    # await mongodb.engine.save(bookdata)
    return templates.TemplateResponse("index.html", {"request": request, "q": q})


@app.on_event("startup")
def on_app_start():
    mongodb.connect()


@app.on_event("shutdown")
def on_app_shutdown():
    mongodb.close()
