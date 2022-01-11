from odmantic import Model


class BookModel(Model):
    keyword: str
    title: str
    publisher: str
    price: int
    image: str

    class Config:
        collection = "book3"
