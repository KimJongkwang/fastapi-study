# 현재는 연습단계
# 추후 예외가 수 백개 이상 많아지게 되면, 데이터베이스에서 관리
# 예외를 백엔드에서 관리하는 것이 프론트엔드에서 UX차원에서 좋을 것 같다?

from common.consts import MAX_API_KEY, MAX_API_WHITELIST


class StatusCode:
    HTTP_500 = 500
    HTTP_400 = 400
    HTTP_401 = 401
    HTTP_403 = 403
    HTTP_404 = 404
    HTTP_405 = 405


class APIException(Exception):
    status_code: int
    code: str  # custom error code(개발자에게 주는 코드)
    msg: str  # user에게 주는 메시지
    detail: str  # error의 정보
    ex: Exception

    def __init__(
        self,
        *,
        status_code: int = StatusCode.HTTP_500,
        code: str = "000000",
        msg: str = None,
        detail: str = None,
        ex: Exception = None,
    ):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        self.detail = detail
        self.ex = ex
        super().__init__(ex)

    @staticmethod
    async def exception_handler(error: Exception):
        """
        에러 로깅을 위해 함수 수정
        기존 APIException 만 처리 --> Exception을 받아 APIException으로 변환
        또는 Exception 반환
        """
        if not isinstance(error, APIException):
            error = APIException(ex=error, detail=str(error))
        return error


class NotFoundUserEx(APIException):
    def __init__(self, user_id: int = None, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_404,
            msg="해당 유저를 찾을 수 없습니다.",
            detail=f"Not Found User ID : {user_id}",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )


class NotAuthorized(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_401,
            msg="로그인이 필요한 서비스 입니다.",
            detail="Authorization Required",
            code=f"{StatusCode.HTTP_401}{'1'.zfill(4)}",
            ex=ex,
        )


class TokenExpiredEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg="세션이 만료되어 로그아웃 되었습니다.",
            detail="Token Expired",
            code=f"{StatusCode.HTTP_400}{'1'.zfill(4)}",
            ex=ex,
        )


class TokenDecodeEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg="비정상적인 접근입니다.",
            detail="Token has been compromised.",
            code=f"{StatusCode.HTTP_400}{'2'.zfill(4)}",
            ex=ex,
        )


class MaxKeyCountEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"API 키 생성은 {MAX_API_KEY}개 까지 가능합니다.",
            detail="Max Key Count Reached",
            code=f"{StatusCode.HTTP_400}{'4'.zfill(4)}",
            ex=ex,
        )


class MaxWLCountEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"API 키 생성은 {MAX_API_WHITELIST}개 까지 가능합니다.",
            detail="Max Whitelist Count Reached",
            code=f"{StatusCode.HTTP_400}{'5'.zfill(4)}",
            ex=ex,
        )


class NoKeyMatchEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_404,
            msg="해당 키에 대한 권한이 없거나 해당 키가 없습니다.",
            detail="No Keys Matched",
            code=f"{StatusCode.HTTP_404}{'3'.zfill(4)}",
            ex=ex,
        )


class InvalidIpEx(APIException):
    def __init__(self, ip: str, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg=f"{ip}는 올바른 IP가 아닙니다.",
            detail=f"inavlid ip : {ip}",
            code=f"{StatusCode.HTTP_400}{'3'.zfill(4)}",
            ex=ex,
        )


class APIQueryStringEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg="쿼리스트링은 key, timestamp 2개만 허용되며, 2개 모두 요청시 제출되어야 합니다.",
            detail="Query String Only Accept key and timestamp.",
            code=f"{StatusCode.HTTP_400}{'7'.zfill(4)}",
            ex=ex,
        )


class APIHeaderInvalidEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg="헤더에 키 해싱된 Secret 이 없거나, 유효하지 않습니다.",
            detail="Invalid HMAC secret in Header",
            code=f"{StatusCode.HTTP_400}{'8'.zfill(4)}",
            ex=ex,
        )


class NotFoundAccessKeyEx(APIException):
    def __init__(self, api_key: str, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_404,
            msg="API 키를 찾을 수 없습니다.",
            detail=f"Not found such API Access Key : {api_key}",
            code=f"{StatusCode.HTTP_404}{'10'.zfill(4)}",
            ex=ex,
        )


class APITimestampEx(APIException):
    def __init__(self, ex: Exception = None):
        super().__init__(
            status_code=StatusCode.HTTP_400,
            msg="쿼리스트링에 포함된 타임스탬프는 KST 이며, 현재 시간보다 작아야 하고, 현재시간 - 10초 보다는 커야 합니다.",
            detail="timestamp in Query String must be KST, Timestamp must be less than now, and greater than now - 10.",
            code=f"{StatusCode.HTTP_400}{'9'.zfill(4)}",
            ex=ex,
        )
