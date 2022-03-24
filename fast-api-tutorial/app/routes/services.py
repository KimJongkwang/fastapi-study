import os
import json
import requests

from fastapi import Request, APIRouter
from fastapi.logger import logger
from common._key import KAKAO_KEY
from errors import exceptions as ex
from models import KakaoMsgBody, MessageOk

router = APIRouter(prefix="/services")


@router.get("")
async def get_all_service(request: Request):
    return dict(your_email=request.state.user.email)


@router.post("kakao/send")
async def send_kakao(request: Request, body: KakaoMsgBody):
    # environ: 시스템 환경변수 추가(KAKAO_KEY 추가없을 경우 _key에서 가져옴.)
    token = os.environ.get("KAKAO_KEY", KAKAO_KEY)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}
    if len(body.msg) >= 200:
        raise ex.OverCharLongEx()

    # LINK 버튼이 안넘어간다. TEXT만 넘어가는데, 원인을 찾아보자.
    body = dict(object_type="text", text=body.msg, link=dict(web_url="https://velog.io/@ceaseless", mobile_url="https://velog.io/@ceaseless"), button_title="지금 확인")
    data = {"template_object": json.dumps(body, ensure_ascii=False)}

    res = requests.post("https://kapi.kakao.com/v2/api/talk/memo/default/send", headers=headers, data=data)
    try:
        res.raise_for_status()
        if res.json()["result_code"] != 0:
            raise Exception("KAKAO SEND FAILED")
    except Exception as e:
        print(res.json())
        logger.warning(e)
        raise ex.KakaoSendFailureEx

    return MessageOk()
