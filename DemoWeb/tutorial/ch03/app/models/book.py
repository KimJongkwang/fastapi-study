# 하나의 도큐먼트(모델, 스키마 등등)
from odmantic import Model


class BookModel(Model):
    keyword: str
    publisher: str
    price: int
    image: str

    # odm 모델안의 컬럼명 정의(json key 정의)
    # Config = collection(table과 같이 이해 됨)
    class Config:
        collection = "books"
