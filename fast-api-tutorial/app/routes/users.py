from os import access
import string
import secrets
from uuid import uuid4
from typing import List

from fastapi import APIRouter, Depends, Request

import models as m
from sqlalchemy.orm import Session
from database.schema import Users, ApiKeys
from database.conn import db

from common.consts import MAX_API_KEY, MAX_API_WHITELIST
from errors import exceptions as ex

router = APIRouter()


# response_model을 안 넣게되면, user.id 로 조회되는 모든 컬럼 전송
# @router.get("/me")
# async def get_user(request: Request, session: Session = Depends(db.session)):
# 위의 파라미터로 db session을 받으면,
# filter(session)로 사용할 수 있는데,
# DB를 한번만 가져와 사용할 경우 굳이 여러개 세션을 사용할 필요가 없음
# 지속적인 DB작업이 필요하다면 session을 새로 받아오는 것도 방법
@router.get("/me")
async def get_me(request: Request):
    """
    get my info
    """
    user = request.state.user
    print(user.id)
    # user_info = Users.get(id=user.id)
    user_info = Users.filter(id__gt=user.id).order_by("email").count()  # 이건 장고스타일
    # user_info = session.query(Users).filter(Users.id > user.id).order_by(Users.email.asc()).count()  # sql alchemy 스타일
    # from errors.exceptions import NotFoundUserEx
    # raise NotFoundUserEx(user_info.email) # 에러처리 테스트
    return user_info

@router.put("/me")
async def put_me(request: Request):
    ...

@router.delete("/me")
async def delete_me(request: Request):
    ...

@router.get("/apikeys", response_model=List[m.GetApiKeyList])
async def get_api_keys(request: Request):
    """
    API KEY 조회
    """
    print(request.state)
    user = request.state.user
    api_keys = ApiKeys.filter(user_id=user.id).all()
    return api_keys

@router.post("/apikeys", response_model=m.GetApiKeys)
async def create_api_keys(request: Request, key_info: m.AddApiKey, session: Session = Depends(db.session)):
    """
    API KEY 생성

    Args:
        request (Request): _description_
        key_info (m.AddApiKey): _description_
        session (Session, optional): _description_. Defaults to Depends(db.session).
    """
    user = request.state.user

    api_keys = ApiKeys.filter(session, user_id=user.id, status="active").count()
    if api_keys == MAX_API_KEY:
        raise ex.MaxKeyCountEx()

    alphabet = string.ascii_letters + string.digits
    s_key = "".join(secrets.choice(alphabet) for _ in range(40))
    uid = None
    while not uid:
        uid_candidate = f"{str(uuid4())[:-12]}{str(uuid4())}"
        print(uid_candidate, " /  API KEY 생성하다 @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@")
        uid_check = ApiKeys.get(access_key=uid_candidate)
        if not uid_check:
            uid = uid_candidate

    key_info = key_info.dict()
    new_key = ApiKeys.create(session, auto_commit=True, secret_key=s_key, user_id=user.id, access_key=uid, **key_info)
    return new_key

# @router.put("/apikeys", response_model=m.GetApiKeyList)



@router.get("/apikeys/{key_id}/whitelists")
async def get_api_keys():
    ...
