from typing import Optional

from fastapi import FastAPI

app = FastAPI()  # FastAPI 라는 클래스를 가져와 app이라는 인스턴스 생성
# 싱글톤 패턴:


@app.get("/")
def read_root():
    print("Hello world")
    return {"Hello": "World"}


@app.get("/hello")
def read_fastapi_hello():
    return {"Hello": "Fastapi"}


# 동적라우팅: 변수에 담아
@app.get("/items/{item_id}/{xyz}")
def read_time(item_id: int, xyz: str, q: Optional[str] = None):
    return {"item_id": item_id, "q": q, "xyz": xyz}
