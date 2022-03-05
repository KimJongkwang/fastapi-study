# 들어오는 요청에 대해 토큰 검사, API 요청에서 헤더의 엑세스 토큰 검사
# API가 아니라 템플릿에서 렌더링이 요구되는 상황에서는 쿠키의 토큰 검사
import time
import typing
import re
import jwt

from fastapi.responses import JSONResponse
from pydantic import Json
from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.types import ASGIApp, Receive, Scope, Send

from common import consts
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
        # None 을 넣지 않으면 호출시에 인풋 에러 발생
        request.state.start = time.time()
        request.state.inspect = None  # 500 error 시 로깅하기위해 사용함 --> SENTRY 사용함
        request.state.user = None  # Token decode 하고 user 데이터를 넣음  --> JWT를 사용하는 이유: user 인증상태를 endpoint 마다 DB를 조회하여 검사하는 것을 지양
        request.state.is_admin_access = None
        ip_from = request.headers["x-forwarded-for"] if "x-forwarded-for" in request.headers.keys() else None
        # x-forwarded-for << aws에서는 load balancer 를 지나면서 고객의 ip가 "x-forwarded-for" 헤더가 추가됨
        # 수집을 한다면, 약관 체크 필요

        if await self.url_pattern_check(request.url.path, self.except_path_regex) or request.url.path in self.except_path_list:
            return await self.app(scope, receive, send)  # check 예외 url 이라면, 요청을 funcion level로 전달

        if request.url.path.startswith("/api"):
            # api 인경우 헤더로 토큰 검사
            if "Authorization" in request.headers.keys():
                request.state.user = await self.token_decode(access_token=request.headers.get("Authorization"))
                # 토큰 없음
            else:
                if "Authorization" not in request.headers.keys():
                    response = JSONResponse(status_code=401, content=dict(msg="Authorization Required"))
                    return await response(scope, receive, send)

        else:
            print(request.cookies)
            # request.cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTEsImVtYWlsIjoia2prNjY0NkBuYXZlci5jb20iLCJuYW1lIjpudWxsLCJwaG9uZV9udW1iZXIiOm51bGwsInByb2ZpbGVfaW1nIjpudWxsLCJzbnNfdHlwZSI6bnVsbH0.DZYxrWuaaUIfRIPcYGfrwxMtKjRMl8vVtW754PRThGs"
            if "Authorization" not in request.cookies.keys():
                response = JSONResponse(status_code=401, content=dict(msg="Authorization Required"))
                return await response(scope, receive, send)

            request.state.user = await self.token_decode(access_token=request.cookies.get("Authorization"))

        request.state.req_time = D.datetime()
        print(D.datetime())
        print(D.date())
        print(D.date_num())

        print(request.cookies, "this is cookies")
        print(headers)
        res = await self.app(scope, receive, send)
        return res

    @staticmethod
    async def url_pattern_check(path, pattern):
        """
        토큰 검사 예외 url 체크

        Args:
            path (_type_): _description_
            pattern (_type_): _description_

        Returns:
            _type_: _description_
        """
        result = re.match(pattern, path)
        if result:
            return True
        return False

    @staticmethod
    async def token_decode(access_token):
        try:
            access_token = access_token.replace("Bearer ", "")
            payload = jwt.decode(access_token, key=consts.JWT_SECRET, algorithms=[consts.JWT_ALGORITHM])
        except jwt.PyJWKError as e:
            print(e)

        return payload
