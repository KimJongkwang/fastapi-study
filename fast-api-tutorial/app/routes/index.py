from datetime import datetime

from fastapi import APIRouter, Response, Request
from inspect import currentframe as frame


# Depends: FastAPI 내장 의존성 주입 메서드
# 의존성 주입의 장점
#     동일한 공유 로직 재사용,
#     데이터베이스 연결 공유,
#     인증 및 보안 기능 시행,
#     그리고 더 많은 것,
#     Flask에서 FastAPI로 원활하게 마이그레이션,
#     FastAPI의 메타 데이터 및 추가 응답, # verify
#     4 FastAPI의 유용한 고급 기능,
#     FastAPI에서 업로드 된 파일을 저장하는 방법,
#     Bash 스크립트로 FastAPI를 다시 시작하는 방법,
#     FastAPI : 들어오는 요청을 일괄 처리하는 방법

router = APIRouter()


@router.get("/")
async def index():
# async def index(session: Session = Depends(db.session), ):
    """
    ELB 상태 체크 API
    """

    # 기본 orm insert 구문
    # user = Users(status="active", name="김종광")
    # session.add(user)
    # session.commit()

    # 함수로 관리
    # Users().create(session, auto_commit=True, name="김종광2")

    current_time = datetime.utcnow()
    return Response(f"Notificaton API (UTC: {current_time.strftime('%Y%m%d%H%M%S')})")


@router.get("/test")
async def test(request: Request):
    """
    ELB 상태 체크 API 테스트
    """
    # 이슈 !! zero division error를 예외처리에서 잡지 못한다.
    # 왜 일까.
    try:
        a = 1 / 0
    except Exception as e:
        request.state.inspect = frame()
        raise e
        # inspect 핸들링되지 않은 에러가 있을 법한 곳에서 사용한다
        # frame() : 파이썬 inspect 모듈의 currentframe 함수, 현재의 위치 등등을 기록

    current_time = datetime.utcnow()
    return Response(f"Notificaton API (UTC: {current_time.strftime('%Y%m%d%H%M%S')})")
