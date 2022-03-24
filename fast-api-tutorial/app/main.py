# base
from dataclasses import asdict
from sys import prefix

# fastapi
import uvicorn
from fastapi import FastAPI, Depends
from fastapi.security import APIKeyHeader

# middleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware
from middlewares.token_validator import access_control
from middlewares.trusted_hosts import AddExceptPathTHM
# from middlewares.trusted_hosts import TrustedHostMiddleware  # AddExceptPathTHM로 재정의

# routes
from routes import index, auth, users, services

# configuration
from database.conn import db
from common.config import conf

# APIKeyHeader: FastAPI swagger가 만들어주는 apikeyheader ui 및 헤더
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

    # 레디스 이니셜라이즈

    # 미들웨어 정의
    # app.add_middleware(AccessControl, except_path_list=EXCEPT_PATH_LIST, except_path_regex=EXCEPT_PATH_REGEX)
    app.add_middleware(middleware_class=BaseHTTPMiddleware, dispatch=access_control)
    # CORS: abc.com 이라면 abc 에서만 접속 가능하도록.
    # 삽질 포인트,, app이 미들웨어를 추가하는데 순서가 중요.
    # 가장 아래의 미들웨어부터 실행한다.
    # 이상이 없으면 아래서부터 위로 올라가면서 미들웨어를 실행함
    # AccessControl 이전 CORS에서는 token이 발행되지 않음 따라서 Access가 먼저 오면 미들웨어 검사가 안됨 --- 이부분은 영상 다시 보고 정리해보자
    app.add_middleware(
        CORSMiddleware,
        allow_origins=conf().ALLOW_SITE,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # except_path = AWS Load balancer에서 health check(모니터링)을 위해 /health url 검사 제외
    # 기존의 starlette의 trustedhostmiddleware는 except path가 없어 새로 정의함
    app.add_middleware(AddExceptPathTHM, allowed_hosts=conf().TRUSTED_HOSTS, except_path=["/health", "*"])

    # 라우터 정의
    app.include_router(index.router, tags=["Root"])
    app.include_router(auth.router, tags=["Authentication"], prefix="/api")
    app.include_router(users.router, tags=["Users"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])  # router 추가시 dependencies로 토큰 검사 필요시 apikey header에 의존성 주입
    if conf().DEBUG:
        app.include_router(services.router, tags=["Services"], prefix="/api", dependencies=[Depends(API_KEY_HEADER)])
    else:
        app.include_router(services.router, tags=["Services"], prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=80, reload=True)
