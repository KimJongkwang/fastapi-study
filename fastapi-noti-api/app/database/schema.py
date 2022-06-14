from sqlalchemy.schema import Column
from sqlalchemy import ForeignKey, Integer, DateTime, func, Enum, String, Boolean
from sqlalchemy.orm import Session, relationship
from database.conn import db

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)  # index = auto_increment
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

    def __init__(self) -> None:
        """
        sql alchemy에서 class를 만들 때, declarative_base에서 잡아주는지는 모르겠으나,
        __init__, __new__ 등을 실행하지 않음.
        현재의 __init__은 아래 CRUD에서 사용되는 변수들을 명시하기 위해 작성
        """
        self._q = None
        self._session = None

    def all_columns(self):
        return [c for c in self.__table__.columns if c.primary_key is False and c.name != "created_at"]

    def __hash__(self) -> int:
        return hash(self.id)

    @classmethod
    def create(cls, session: Session, auto_commit=False, **kwagrs):
        """
        테이블 데이터 적재 전용 함수
        Args:
            session (Session): DB 세션
            auto_commit (bool, optional): 자동커밋 여부
            kwagrs: 적재할 데이터들
        """
        obj = cls()
        for col in obj.all_columns():
            col_name = col.name
            if col_name in kwagrs:
                setattr(obj, col_name, kwagrs.get(col_name))
        session.add(obj)
        session.flush()
        if auto_commit:
            session.commit()
        return obj

    @classmethod
    def get(cls, session: Session = None, **kwagrs):
        """
        Simply get a row
        """
        _session = next(db.session()) if not session else session
        query = _session.query(cls)
        for key, val in kwagrs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        result = query.first()
        if not session:
            _session.close()
        return result

    @classmethod
    def filter(cls, session: Session = None, **kwargs):
        """
        Simply get many Row

        gt: greater than
        e: equal
        lt: less than
        in: or

        Args:
            session (Session, optional): _description_. Defaults to None.
        """
        cond = []
        for key, val in kwargs.items():
            key = key.split("__")
            if len(key) > 2:
                raise Exception("No 2 more dunders")
            col = getattr(cls, key[0])
            if len(key) == 1:
                cond.append((col == val))
            elif len(key) == 2 and key[1] == "gt":
                cond.append((col > val))
            elif len(key) == 2 and key[1] == "gte":
                cond.append((col >= val))
            elif len(key) == 2 and key[1] == "lt":
                cond.append((col < val))
            elif len(key) == 2 and key[1] == "lte":
                cond.append((col <= val))
            elif len(key) == 2 and key[1] == "in":
                cond.append((col.in_(val)))
        obj = cls()
        if session:
            obj._session = session
            obj._sess_served = True
        else:
            obj._session = next(db.session())
            obj._sess_served = False
        query = obj._session.query(cls)
        query = query.filter(*cond)
        obj._q = query
        return obj

    @classmethod
    def cls_attr(cls, col_name=None):
        if col_name:
            col = getattr(cls, col_name)
            return col
        else:
            return cls

    def order_by(self, *args: str):
        for a in args:
            # startswith "-" 로 asc, desc 구분
            if a.startswith("-"):
                col_name = a[1:]
                is_asc = False
            else:
                col_name = a
                is_asc = True
            col = self.cls_attr(col_name)
            self._q = self._q.order_by(col.asc()) if is_asc else self._q.order_by(col.desc())
        return self

    def update(self, auto_commit: bool = False, **kwargs):
        qs = self._q.update(kwargs)
        get_id = self.id
        ret = None

        self._session.flush()
        if qs > 0 :
            ret = self._q.first()
            self._session.expunge(ret)
        if auto_commit:
            self._session.commit()
        return ret

    def first(self):
        result = self._q.first()
        self.close()
        return result

    def delete(self, auto_commit: bool = False, **kwagrs):
        self._q.delete()
        if auto_commit:
            self._session.commit()

    def all(self):
        result = self._q.all()
        self.close()
        return result

    def count(self):
        result = self._q.count()
        self.close()
        return result

    def close(self):
        if self._sess_served:
            self._session.commit()
            self._session.close()
        else:
            self._session.flush()


class Users(Base, BaseMixin):
    __tablename__ = "users"

    status = Column(Enum("active", "deleted", "blocked"), default="active")
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=True)
    keys = relationship("ApiKeys", back_populates="users")


class ApiKeys(Base, BaseMixin):
    __tablename__ = "api_keys"

    access_key = Column(String(length=64), nullable=False, index=True)
    secret_key = Column(String(length=64), nullable=False)
    user_memo = Column(String(length=40), nullable=True)
    status = Column(Enum("active", "deleted", "blocked"), default="active")
    is_whitelisted = Column(Boolean, default=False)  # api 로 받아낼 수 있는 IP주소
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    whitelist = relationship("ApiWhiteLists", backref="api_keys")
    users = relationship("Users", back_populates="keys")


class ApiWhiteLists(Base, BaseMixin):
    __tablename__ = "api_whitelists"

    ip_addr = Column(String(length=64), nullable=False)
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False)
