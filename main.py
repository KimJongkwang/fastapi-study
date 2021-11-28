from fastapi import FastAPI
from pydantic.main import BaseModel

class HelloWorldRequest(BaseModel):
    name: str
    age: int


app = FastAPI()

@app.get("/")
async def root():
    return {"Hello": "World"}

@app.get("/hello/{name}")
async def hello_with_name(name: str):
    return "Hello with name. your name is " + name

@app.get("/hello2/query")
async def hello_with_querystring(name: str):
    return "Hello with name. your name is " + name

@app.post("/hello3/post")
async def hello_post(request: HelloWorldRequest):
    return "hello with post. your name: {}, your age: {}".format(request.name, request.age)