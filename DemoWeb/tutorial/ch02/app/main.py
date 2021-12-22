from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse

# from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent


app = FastAPI()

# app.mount: 미들웨어
# app.mount("/static", StaticFiles(directory="static"), name="static")
# Static Files(정적 파일 관리)를 관리하는 미들웨어

# templates html파일 서빙 위치 지정
# directory는 절대경로로 설정하여 하는것이 좋음
# Jinja2는 요청 응답을 템플릿에 전달하도록 할 수 있게끔 하는 템플릿 엔진
templates = Jinja2Templates(directory=BASE_DIR / "templates")


# response를 html로 서빙
# {id}: dynamic url
# 라우터 인자는 반드시 타입힌팅이 필요(없을 시 에러)
@app.get("/items/{id}", response_class=HTMLResponse)
async def read_item(request: Request, id: str):
    # request는 요청하는 주체에 대한 정보를 담는 것
    print(request["headers"])
    data = {"request": request, "id": id, "data": "data"}
    return templates.TemplateResponse("item.html", data)
