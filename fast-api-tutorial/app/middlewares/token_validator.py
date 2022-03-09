# 들어오는 요청에 대해 토큰 검사, API 요청에서 헤더의 엑세스 토큰 검사
# API가 아니라 템플릿에서 렌더링이 요구되는 상황에서는 쿠키의 토큰 검사
import time
import re
import jwt

# from fastapi.responses import JSONResponse
from starlette.requests import Request
from starlette.responses import JSONResponse
from common.consts import (
    EXCEPT_PATH_REGEX, EXCEPT_PATH_LIST,
    JWT_SECRET, JWT_ALGORITHM
)
from models import UserToken
from utils.date_utils import D
from utils.logger import api_logger
from errors import exceptions as ex
from errors.exceptions import APIException


async def access_control(request: Request, call_next):
    """
    토큰검사 미들웨어

    Args:
        request (Request): 사용자 요청
        call_next (_type_): 다음 함수, 또는 다음 미들웨어

    Returns:
        _type_: 검사 이상유무 반환
                이상없을 경우, response(call_next) 반환
                이상있을 경우, 에러 발생
    """
    request.state.req_time = D.datetime()
    request.state.start = time.time()
    request.state.inspect = None  # 500 error 시 로깅하기위해 사용함 --> SENTRY 사용함
    request.state.user = None  # Token decode 하고 user 데이터를 넣음  --> JWT를 사용하는 이유: user 인증상태를 endpoint 마다 DB를 조회하여 검사하는 것을 지양
    ip = (
        request.headers["x-forwarded-for"]
        if "x-forwarded-for" in request.headers.keys()
        else request.client.host
    )
    request.state.ip = ip.split(",")[0] if "," in ip else ip
    headers = request.headers
    cookies = request.cookies
    url = request.url.path
    if await url_pattern_check(url, EXCEPT_PATH_REGEX) or url in EXCEPT_PATH_LIST:
        response = await call_next(request)
        if url != "/":
            await api_logger(request=request, response=response)
        return response

    try:
        if url.startswith("/api"):
            # api 인 경우 헤더로 토큰 검사
            if "authorization" in headers.keys():
                token_info = await token_decode(access_token=headers.get("Authorization"))
                request.state.user = UserToken(**token_info)
            else:
                if "Authorization" not in headers.keys():
                    raise ex.NotAuthorized()
        else:
            # 템플릿 렌더링인 경우 cookies 토큰 검사
            cookies["Authorization"] = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MTEsImVtYWlsIjoia2prNjY0NkBuYXZlci5jb20iLCJuYW1lIjpudWxsLCJwaG9uZV9udW1iZXIiOm51bGwsInByb2ZpbGVfaW1nIjpudWxsLCJzbnNfdHlwZSI6bnVsbH0.DZYxrWuaaUIfRIPcYGfrwxMtKjRMl8vVtW754PRThGs"

            if "Authorization" not in cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)

        # call_next() 이전에 미들웨어 level에서 검사 실행(if, else)
        # 이후 call_next()로 API 실행
        response = await call_next(request)
        await api_logger(request=request, response=response)

    except Exception as e:
        error = await ex.APIException.exception_handler(e)
        error_dict = dict(status=error.status_code, msg=error.msg, detail=error.detail, code=error.code)
        response = JSONResponse(status_code=error.status_code, content=error_dict)
        await api_logger(request=request, error=error)

    return response


async def url_pattern_check(path, pattern):
    result = re.match(pattern, path)
    if result:
        return True
    return False


async def token_decode(access_token):
    try:
        access_token = access_token.replace("Bearer ", "")
        payload = jwt.decode(access_token, key=JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise ex.TokenExpiredEx()
    except jwt.DecodeError:
        raise ex.TokenDecodeEx()
    # except jwt.PyJWKError as e:
    #     print(e)
    return payload
