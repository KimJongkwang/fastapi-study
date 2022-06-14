import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

import pytest
from typing import List
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import create_app
from app.database.conn import db, Base
from app.database.schema import Users
from app.routes.auth import create_access_token
from app.models import UserToken


@pytest.fixture(scope="session")
def app():
    os.environ["API_ENV"] = "test"
    return create_app()


@pytest.fixture(scope="session")
def client(app):
    Base.metadata.create_all(db.engine)
    return TestClient(app=app)


@pytest.fixture(scope="function", autouse=True)
def session():
    sess = next(db.session())
    yield sess
    clear_all_table_data(
        session=sess,
        metadata=Base.metadata,
        except_tabels=[]
    )
    sess.rollback()


@pytest.fixture(scope="function")
def login(session):
    """
    테스트전 사용자 미리 등록
    """
    db_user = Users.create(session=session, email="kjk6646@naver.com", pw="123")
    session.commit()
    access_token = create_access_token(data=UserToken.from_orm(db_user).dict(exclude={"pw", "marketing_agree"}),)
    return dict(Authorization=f"Bearer {access_token}")


def clear_all_table_data(session: Session, metadata, except_table: List[str] = None):
    session.execute("SET FOREIGN_KEY_CHECKS = 0;")
    for table in metadata.sorted_tables:
        if table.name not in except_table:
            session.execute(table.delete())
    session.exceute("SET FOREIGN_KEY_CHECKS = 1;")
    session.commit()
