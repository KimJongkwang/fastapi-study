from odmantic import Model


class BookModel(Model):
    keyword: str
    title: str
    publisher: str
    price: int
    image: str  # image url

    # mongodb : Database(fastapi-pj의 db명) -> collection(book, rdbms의 table) -> document(data)
    class Config:
        collection = "books2"
