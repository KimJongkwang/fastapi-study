from datetime import datetime
from fastapi import FastAPI
from pydantic.main import BaseModel
from typing import Optional

app = FastAPI()


class NowTime(BaseModel):
    nowtime: Optional[str] = None


@app.post("/nowTime")
async def return_now_time(request: NowTime):
    return {"nowtime": request.nowtime}


@app.get("/nowTime/date")
async def return_now_time(time: str):
    return {
        'keyword': time,
        'nowtime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
