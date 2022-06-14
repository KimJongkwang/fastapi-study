from msilib import schema
from fastapi import FastAPI
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import logging


def _database_exist(engine, schema_name):
    query = f"""
        SELECT schema_name FROM information_schema.schema WHERE schema_name = '{schema_name}';
    """
    with engine.connect() as conn:
        result_proxy = conn.execute(query)
        result = result_proxy.scalar()
        return bool(result)


def _drop_database(engine, schema_name):
    with engine.connect() as conn:
        conn.execute(
            f"DROP DATABASE {schema_name};"
        )


def _create_database(engine, schema_name):
    with engine.connect() as conn:
        conn.execute(
            f"CREATE DATABASE {schema_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;"
        )


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
        pool_recycle = kwargs.setdefault("DB_POOL_RECYCLE", 900)
        is_testing = kwargs.setdefault("TEST_MODE", False)
        echo = kwargs.setdefault("DB_ECHO", True)

        self._engine = create_engine(
            database_url,
            echo=echo,
            pool_recycle=pool_recycle,  # DB 커넥트 시간초과 시 연결 해제 기본 900초 설정
            pool_pre_ping=True,  # 사전 핑 테스트
        )
        if is_testing:
            db_url = self._engine.url
            if db_url.host != "localhost":
                raise Exception("db host must be 'localhost' in test environment")
            except_schema_db_url = f"{db_url.drivername}://{db_url.username}@{db_url.host}"
            schema_name = db_url.database
            temp_engine = create_engine(
                except_schema_db_url,
                echo=echo,
                pool_recycle=pool_recycle,
                pool_pre_ping=True,
            )
            if _database_exist(temp_engine, schema_name):
                _drop_database(temp_engine, schema_name)
            _create_database(temp_engine, schema_name)
            temp_engine.dispose()
        self._session = sessionmaker(autocommit=False, autoflush=False, bind=self._engine)

        @app.on_event("startup")
        def startup():
            self._engine.connect()
            logging.info("DB connected.")

        @app.on_event("shutdown")
        def shutdown():
            self._session.close_all()
            self._engine.dispose()
            logging.info("DB disconnected")

    def get_db(self):
        """
        요청마다 DB 세션 유지 함수
        """
        if self._session is None:
            raise Exception("Must be called 'init_app'")
        db_session = None

        try:
            db_session = self._session()
            yield db_session
        finally:
            db_session.close()

    @property
    def session(self):
        return self.get_db

    @property
    def engine(self):
        return self._engine


db = SQLAlchemy()
Base = declarative_base()
