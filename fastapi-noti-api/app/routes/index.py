from pathlib import Path
from datetime import datetime
from aiohttp import request


from fastapi import APIRouter, Response, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from inspect import currentframe as frame


BASE_DIR = Path(__file__).resolve().parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
print(templates)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    ELB 상태 체크 API
    """
    current_time = datetime.utcnow()
    return templates.TemplateResponse("./index.html", context=dict(request=request, item=f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})"))


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크 API 테스트
    """
    current_time = datetime.utcnow()
    return Response(f"Notification API (UTC: {current_time.strftime('%Y.%m.%d %H:%M:%S')})")
