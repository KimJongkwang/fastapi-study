from typing import Optional
from dataclasses import asdict

import uvicorn
from fastapi import FastAPI

# from app.common.config import conf
from common.config import conf


def create_app():
    """
    앱 함수 실행
    """
    c = conf()
    app = FastAPI()

    conf_dict = asdict(c)
    print(conf_dict)
    db.init_app(app, **conf_dict)

    # 데이터 베이스 이니셜라이즈

    # 레디스 이니셜라이즈

    # 미들웨어 정의

    # 라우터 정의

    return app


app = create_app()
