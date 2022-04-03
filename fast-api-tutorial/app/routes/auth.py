from datetime import datetime, timedelta
import bcrypt
import jwt

from fastapi import APIRouter, Depends
from pydantic import JsonError

from sqlalchemy.orm import Session  # Session 타이핑을 위해
from starlette.responses import JSONResponse

from common.consts import JWT_SECRET, JWT_ALGORITHM  # JWT는 KEY를 받아 인코드 -> 디코드 사용자 토큰 검증
from database.conn import db
from database.schema import Users
from models import SnsType, Token, UserToken, UserRegister

# TODO:
"""
1. SNS 로그인을 위한 각 SNS 앱 및 개발자 도구 준비(G, F, K)
2. 이메일, 비밀번호로 가입
3. 가입된 이메일, 비밀번호로 로그인
4. JWT 발급
"""

router = APIRouter(prefix="/auth")


@router.post("/register/{sns_type}", status_code=200, response_model=Token)
async def register(sns_type: SnsType, reg_info: UserRegister, session: Session = Depends(db.session)):
    # FastAPI 내 docs string에서는 ``을 넣으면 swagger에서 코드블럭 잡아줌
    """
    `회원가입 API`

    Args:
        sns_type (SnsType):
        reg_info (models.UserRegister):
        session (Session, optional): . Defaults to Depends(db.session).
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(reg_info.email)
        if not reg_info.email or not reg_info.pw:
            # 추후에는 미들웨어에서 400에러를 처리하도록 수정
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided"))
        if is_exist:
            return JSONResponse(status_code=400, content=dict(msg="EMAIL_EXISTS"))
        hash_pw = bcrypt.hashpw(reg_info.pw.encode("utf-8"), bcrypt.gensalt())  # bcrypt: hash 함수 pw를 hash로 변환 및 검증하기 위해 사용
        new_user = Users.create(session, auto_commit=True, pw=hash_pw, email=reg_info.email)
        # 토큰 생성, 패스워드와 마케팅동의는 토큰생성에 제외
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(new_user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="Not supported"))


@router.post("/login/{sns_type}", status_code=200)
async def login(sns_type: SnsType, user_info: UserRegister, session: Session = Depends(db.session)):
    """
    `Login API`

    Args:
        sns_type (SnsType): _description_
        user_info (UserRegister): _description_
        session (Session, optional): _description_. Defaults to Depends(db.session).
    """
    if sns_type == SnsType.email:
        is_exist = await is_email_exist(user_info.email)
        if not user_info.email or not user_info.pw:
            # 추후에는 미들웨어에서 400에러를 처리하도록 수정
            return JSONResponse(status_code=400, content=dict(msg="Email and PW must be provided"))
        if not is_exist :
            return JSONResponse(status_code=400, content=dict(msg="이메일 또는 비밀번호를 잘못 입력하였습니다."))
        user = Users.get(email=user_info.email)
        is_verified = bcrypt.checkpw(user_info.pw.encode("utf-8"), user.pw.encode("utf-8"))  # checkpw 패스워드 해시값 비교
        if not is_verified:
            return JSONResponse(status_code=400, content=dict(msg="이메일 또는 비밀번호를 잘못 입력하였습니다."))
        # Autorization 고정 틀? Bearer로 토큰을 주는 것..
        token = dict(Authorization=f"Bearer {create_access_token(data=UserToken.from_orm(user).dict(exclude={'pw', 'marketing_agree'}),)}")
        return token
    return JSONResponse(status_code=400, content=dict(msg="Not supported"))


async def is_email_exist(email: str):
    get_email = Users.get(email=email)
    if get_email:
        return True
        # return get_email  # 추후 고려 쿼리중복을 줄이기 위해
    return False


def create_access_token(*, data: dict = None, expires_delta: int = None):
    to_encode = data.copy()
    print(data)
    if expires_delta:
        to_encode.update({"exp": datetime.utcnow() + timedelta(hours=expires_delta)})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return encoded_jwt
