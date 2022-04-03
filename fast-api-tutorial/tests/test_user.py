import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))


from app.database.conn import db
from app.database.schema import Users


def test_create_get_apikey(client, session, login):
    """
    레버 로그인
    :param client:
    :param session:
    :return:
    """
    key = dict(user_memo="jk")
    res = client.post("api/user/apikeys", json=key, headers=login)
    res_body = res.json()
    assert res.status_code == 200
    assert "secret_key" in res_body

    res = client.get("api/user/apikeys", headers=login)
    res_body = res.json()
    assert res.status_code == 200
    assert "jk" in res_body[0]["user_memo"]
