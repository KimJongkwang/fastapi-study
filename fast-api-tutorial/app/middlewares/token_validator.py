# 들어오는 요청에 대해 토큰 검사, API 요청에서 헤더의 엑세스 토큰 검사
# API가 아니라 템플릿에서 렌더링이 요구되는 상황에서는 쿠키의 토큰 검사
import time
import typing

from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from utils.date_utils import D


class AccessControl:
    def __init__(
        self,
        app: ASGIApp,
        except_path_list: typing.Sequence[str] = None,
        except_path_regex: str = None,
    ) -> None:
        if except_path_list is None:
            except_path_list = ["*"]
        self.app = app
        self.except_path_list = except_path_list
        self.except_path_regex = except_path_regex

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        print(self.except_path_regex)
        print(self.except_path_list)

        request = Request(scope=scope)
        headers = Headers(scope=scope)

        request.state.jongkwang = "Made by Jongkwang Kim"
        request.state.req_time = D.datetime()
        print(D.datetime())
        print(D.date())
        print(D.date_num())
        request.state.start = time.time()
        request.state.inspect = None  # 500 error 시 로깅하기위해 사용함 --> SENTRY 사용함
        request.state.user = None  # Token decode 하고 user 데이터를 넣음  --> JWT를 사용하는 이유: user 인증상태를 endpoint 마다 DB를 조회하여 검사하는 것을 지양
        request.state.is_admin_access = None
        print(request.cookies, "this is cookies")
        print(headers)
        res = await self.app(scope, receive, send)
        return res
