from fastapi import APIRouter, Request

from models import UserMe
from database.schema import Users

router = APIRouter()


# response_model을 안 넣게되면, user.id 로 조회되는 모든 컬럼 전송
@router.get("/me", response_model=UserMe)
async def get_user(request: Request):
    """
    get my info
    """
    user = request.state.user
    user_info = Users.get(id=user.id)
    # from errors.exceptions import NotFoundUserEx
    # raise NotFoundUserEx(user_info.email) # 에러처리 테스트
    return user_info
