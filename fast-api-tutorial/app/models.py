from enum import Enum
from typing import List
from datetime import datetime
from pydantic import Field
from pydantic.main import BaseModel
from pydantic.networks import EmailStr
# from pydantic.networks

# models.py: pydantic이 validation 하는 model
# json으로 입력받고, json으로 주는 모든 데이터를 객체화 하기 위해 model class로 정의한다.

class MessageOk(BaseModel):
    message: str = Field(default="OK")


class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None


class SnsType(str, Enum):
    email: str = "email"
    facebook: str = "facebook"
    google: str = "google"
    kakao: str = "kakao"


class Token(BaseModel):
    """
    response Mdoel.
    요청에 따른 토큰을 생성하여 유저에게 준다.

    Args:
        BaseModel (_type_): _description_
    """
    Authorization: str = None

class UserToken(BaseModel):
    """
    Token을 객체화하여 사용하기 위함

    Args:
        BaseModel (_type_): _description_
    """
    id: int
    pw: str = None
    email: str = None
    name: str = None
    phone_number: str = None
    profile_img: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class UserMe(BaseModel):
    id: int
    email: str = None
    name: str = None
    sns_type: str = None

    class Config:
        orm_mode = True


class AddApiKey(BaseModel):
    user_memo: str = None

    class Config:
        orm_mode = True


class GetApiKeyList(AddApiKey):
    id: int = None
    access_key: str = None
    created_at: datetime = None


class GetApiKeys(GetApiKeyList):
    secret_key: str = None


class CreateApiWhiteLists(BaseModel):
    ip_addr: str = None


class GetApiWhiteLists(CreateApiWhiteLists):
    id: int

    class Config:
        orm_mode = True


class KakaoMsgBody(BaseModel):
    msg: str = None


class EmailRecipients(BaseModel):
    name: str
    email: str


class SendEmail(BaseModel):
    email_to: List[EmailRecipients] = None
