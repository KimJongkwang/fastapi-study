from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging


class SQLAlchemy:
    def __init__(self, app: FastAPI = None, **kwargs) -> None:
        self._engine = None
        self._session = None
        if app is not None:
            self.init_app(app=app, **kwargs)

    def init_app(self, app: FastAPI, **kwargs):
        """
        DB 초기화 함수

        Args:
            app (FastAPI): FastAPI 인스턴스
            kwargs: DB 정보
        """
        database_url = kwargs.get("DB_URL")
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900) # dict.get("DB_POOL_RECYCLE", 900)
        echo = kwargs.setdefault("DB_ECHO", True)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,  # DB 커넥트 시간초과 시 연결 해제 기본 900초 설정
            pool_pre_ping=True,  # 사전 핑 테스트
        )

        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine) # 위 엔진으로 세션 생성

        @app.on_event("startup")
        def startup():
            self._engine.connect()
            logging.info("DB connected.")

        
        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected")


        @
        # :param pool_recycle=-1: this setting causes the pool to recycle
        #   connections after the given number of seconds has passed. It
        #   defaults to -1, or no timeout. For example, setting to 3600
        #   means connections will be recycled after one hour. Note that
        #   MySQL in particular will disconnect automatically if no
        #   activity is detected on a connection for eight hours (although
        #   this is configurable with the MySQLDB connection itself and the
        #   server configuration as well).

        # :param pool_pre_ping: boolean, if True will enable the connection pool
        #  "pre-ping" feature that tests connections for liveness upon each checkout.
