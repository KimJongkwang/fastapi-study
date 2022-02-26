
from sqlalchemy.schema import Column
from sqlalchemy import Integer, DateTime, func, Enum, String, Boolean
from sqlalchemy.orm import Session
from database.conn import db

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class BaseMixin:
    id = Column(Integer, primary_key=True, index=True)  # index = auto_increment
    created_at = Column(DateTime, nullable=False, default=func.utc_timestamp())
    updated_at = Column(DateTime, nullable=False, default=func.utc_timestamp(), onupdate=func.utc_timestamp())

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
    def get(cls, **kwagrs):
        """
        Simply get a row

        Raises:
            Exception:

        Returns:
            _type_: _description_
        """
        # obj = cls()
        # get(select)은 commit이 필요 없기 때문에, 추가로 세션을 하나 더 받아온다. 이때 next를 사용하여 return 시 자동으로 세션이 종료되게끔 유도
        session = next(db.session())  # 단, 트래픽이 얼마나 발생할지 여부에 따라 next()로 받는 것보다, parameter로 session을 받아 오는것이 좋을 수 있음
        query = session.query(cls)
        print(query)
        for key, val in kwagrs.items():
            col = getattr(cls, key)
            query = query.filter(col == val)  # filter 정의: 2개 이상 로우를 전달

        if query.count() > 1:
            raise Exception("Only one row is supposed to be returned, but got more than one.")
        return query.first()

    @classmethod
    def filter(cls):
        ...


class Users(Base, BaseMixin):
    __tablename__ = "users"
    status = Column(Enum("active", "deleted", "blocked"), default="active")  # Enum 셋 중 하나만 입력 가능(validation용)
    email = Column(String(length=255), nullable=True)
    pw = Column(String(length=2000), nullable=True)
    name = Column(String(length=255), nullable=True)
    phone_number = Column(String(length=20), nullable=True, unique=True)
    profile_img = Column(String(length=1000), nullable=True)
    sns_type = Column(Enum("FB", "G", "K"), nullable=True)
    marketing_agree = Column(Boolean, nullable=True, default=True)

    """DDL users
    CREATE TABLE users(
    id INT PRIMARY KEY AUTO_INCREMENT,
    status ENUM('active', 'deleted', 'blocked') DEFAULT 'active',
    email VARCHAR(255) NULL,
    pw VARCHAR(2000) NULL,
    name VARCHAR(255) NULL,
    phone_number VARCHAR(20) NULL UNIQUE,
    profile_img VARCHAR(1000) NULL,
    sns_type ENUM('FB', 'G', 'K') NULL,
    marketing_agree TINYINT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,   -- 최초 insert시 시간
    updated_at DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP   -- 업데이트시 현재 시간
    );
    """
