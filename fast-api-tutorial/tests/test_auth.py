import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.database.conn import db
from app.database.schema import Users


def test_registration(client, session):
    """
    레버 로그인

    Args:
        client (_type_): _description_
        session (_type_): _description_
    """

    user = dict(email="kjk6646@naver.com", pw="123", name="jk", phone="01012341234")
    res = client.post("api/auth/register/email", json=user)
    res_body = res.json()
    print(res.json())
    assert res.status_code == 201
    assert "Authorization" in res_body


def test_registration_exist_email(client, session):
    user = dict(email="Halo@gmail.com", pw="123", name="halo", phone="010101001010")
    db_user = Users.create(session=session, **user)
    session.commit()
    res = client.post("api/auth/register/email", json=user)
    res_body = res.json()
    assert res.status_code == 400
    assert "EMAIL_EXISTS" == res_body["msg"]
