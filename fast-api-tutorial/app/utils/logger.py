import json
import logging
import time
from datetime import datetime, timedelta
from fastapi import Request
from fastapi.logger import logger

logger.setLevel(logging.INFO)

async def api_logger(request: Request, response=None, error=None):
    time_format = "%Y/%m/%d %H:%M:%S"
    t = time.time() - request.state.start  # 현재 함수의 런타임 시간
    status_code = error.status_code if error else response.status_code
    error_log = None
    user = request.state.user
    # body = await request.body()  # put, post에서는 body 로그 추가
    if error:
        if request.state.inspect:
            frame = request.state.inspect
            error_file = frame.f_code.co_filename
            error_func = frame.f_code.co_name
            error_line = frame.f_lineno
        else:
            error_func = error_file = error_line = "UNKNOWN"

        error_log = dict(
            errorFunc=error_func,
            location="{} line in {}".format(str(error_line), error_file),
            raised=str(error.__class__.__name__),
            msg=str(error.ex),
        )

    email = user.email.split("@") if user and user.email else None
    user_log = dict(
        client=request.state.ip,
        user=user.id if user and user.id else None,
        email="**" + email[0][2:-1] + "*@" + email[1] if user and user.email else None,  # 개인정보 보호
    )

    log_dict = dict(
        url=request.url.hostname + request.url.path,  # 접근 url
        method=str(request.method),  # 메소드
        statusCode=status_code,  # 에러코드 또는 상태코드
        errorDetail=error_log,
        client=user_log,
        processedTime=str(round(t * 1000, 5)) + "ms",
        datetimeUTC=datetime.utcnow().strftime(time_format),
        datetimeKST=(datetime.utcnow() + timedelta(hours=9)).strftime(time_format),
    )

    # if body:
    #     log_dict["body"] = body
    if error and error.status_code >= 500:
        logger.error(json.dumps(log_dict))  # 500 에러는 error(처리가 안된 에러들)
    else:
        logger.info(json.dumps(log_dict))  # 400 에러는 errors에서 처리된 에러들, 서버입장에서 예외처리된 에러는 info로 볼 수 있다.
