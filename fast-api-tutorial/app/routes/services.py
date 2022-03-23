import os
import json
import requests

from fastapi import Request, APIRouter

from errors import exceptions as ex
from models import KakaoMsgBody, MessageOk

router = APIRouter(prefix="/services")


@router.get("")
async def get_all_service(request: Request):
    return dict(your_email=request.state.user.email)


@router.post("kakao/send")
async def send_kakao(request: Request, body: KakaoMsgBody):
    token = os.environ.get("KAKAO_KEY", "")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/x-www-form-urlencoded"}

    body = dict(object_type="text", text=body.msg, link=dict(web_url="https://naver.com", mobile_url="https://naver.com"), button_title="지금 확인")
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
