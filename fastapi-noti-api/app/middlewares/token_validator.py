import base64
import time
import re
import jwt
import hmac

from starlette.requests import Request
from starlette.responses import JSONResponse
from common.consts import (
    EXCEPT_PATH_REGEX, EXCEPT_PATH_LIST,
    JWT_SECRET, JWT_ALGORITHM
)
from common.config import conf
from database.conn import db
from database.schema import ApiKeys, Users
from models import UserToken
from utils.date_utils import D
from utils.query_utils import to_dict
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
    request.state.inspect = None
    request.state.user = None
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
            if url.startswith("/api/services"):
                # api service에서 jwt 뿐만 아니라 secret key로 검사
                qs = str(request.query_params)
                qs_list = qs.split("&")
                session = next(db.session())

                if not conf().DEBUG:
                    try:
                        qs_dict = {qs_split.split("=")[0]: qs_split.split("=")[1] for qs_split in qs_list}
                    except Exception:
                        raise ex.APIQueryStringEx()

                    qs_keys = qs_dict.keys()

                    if "key" not in qs_keys or "timestamp" not in qs_keys:
                        raise ex.APIQueryStringEx()
                    if "secret" not in headers.keys():
                        raise ex.APIHeaderInvalidEx()

                    api_key = ApiKeys.get(session=session, access_key=qs_dict["key"])

                    if not api_key:
                        raise ex.NotFoundAccessKeyEx(api_key=qs_dict["key"])

                    mac = hmac.new(bytes(api_key.secret_key, encoding="utf8"), bytes(qs, encoding="utf8"), digestmod="sha256")
                    d = mac.digest()
                    validating_secret = str(base64.b64encode(d).decode("utf-8"))
                    if headers["secret"] != validating_secret:
                        raise ex.APIHeaderInvalidEx()

                    # Replay Attack 방지: 10초 이전의 생성한 요청까지만 인증, header의 secret_key를 계속해서 변경하도록 유도
                    now_timestamp = int(D.datetime(diff=9).timestamp())
                    if now_timestamp - 10 > int(qs_dict["timestamp"]) or now_timestamp < int(qs_dict["timestamp"]):
                        raise ex.APITimestampEx()

                    user_info = to_dict(api_key.users)
                    request.state.user = UserToken(**user_info)

                else:
                    if "authorization" in headers.keys():
                        key = headers.get("Authorization")
                        api_key_obj = ApiKeys.get(session=session, access_key=key)
                        user_info = to_dict(Users.get(session=session, id=api_key_obj.user_id))
                        request.state.user = UserToken(**user_info)
                    else:
                        if "Authorization" not in headers.keys():
                            raise ex.NotAuthorized()
                session.close()
                response = await call_next(request)
                return response

            else:
                if "authorization" in headers.keys():
                    token_info = await token_decode(access_token=headers.get("Authorization"))
                    request.state.user = UserToken(**token_info)
                else:
                    if "Authorization" not in headers.keys():
                        raise ex.NotAuthorized()
        else:
            # 템플릿 렌더링인 경우 cookies 토큰 검사
            if "Authorization" not in cookies.keys():
                raise ex.NotAuthorized()

            token_info = await token_decode(access_token=cookies.get("Authorization"))
            request.state.user = UserToken(**token_info)

        # call_next() 이전에 미들웨어 level에서 검사 실행(if, else) 이후 call_next()로 API 실행
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
    return payload
