# base
from dataclasses import asdict

# fastapi
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader

# middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from middlewares.token_validator import access_control
from middlewares.trusted_hosts import AddExceptPathTHM

# routes
from routes import index, auth, users, services

# configuration
from database.conn import db
from common.config import conf

API_KEY_HEADER = APIKeyHeader(name="Authorization", auto_error=False)


def create_app():
    """
    앱 함수 실행
    """
    app = FastAPI()

    # 데이터 베이스 이니셜라이즈
    c = conf()
    conf_dict = asdict(c)
    db.init_app(app, **conf_dict)

    # 미들웨어
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(AddExceptPathTHM, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health", "*"])

    # 라우터
    app.include_router(index.router, tags=["Root"])
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(users.router, tags=["Users"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    if conf().DEBUG:
        app.include_router(services.router, tags=["Services"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    else:
        app.include_router(services.router, tags=["Services"], prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=80, reload=True)
