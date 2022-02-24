# models.py: pydantic이 validation 하는 model

from enum import Enum

from pydantic.main import BaseModel
from pydantic.networks import EmailStr
from dataclasses import dataclass


class UserRegister(BaseModel):
    # pip install 'pydantic[email]'
    email: EmailStr = None
    pw: str = None


@dataclass
class UserRegisterDataClass:
    email: EmailStr = None
    pw: str = None


