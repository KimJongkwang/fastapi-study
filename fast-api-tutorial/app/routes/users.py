from fastapi import APIRouter, Depends, Request

from models import UserMe
from sqlalchemy.orm import Session
from database.schema import Users
from database.conn import db

router = APIRouter()


# response_model을 안 넣게되면, user.id 로 조회되는 모든 컬럼 전송
# @router.get("/me")
# async def get_user(request: Request, session: Session = Depends(db.session)):  
# 위의 파라미터로 db session을 받으면, 
# filter(session)로 사용할 수 있는데, 
# DB를 한번만 가져와 사용할 경우 굳이 여러개 세션을 사용할 필요가 없음
# 지속적인 DB작업이 필요하다면 session을 새로 받아오는 것도 방법
@router.get("/me")
async def get_user(request: Request):
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
