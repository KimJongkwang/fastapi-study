import os
import json
import requests
from time import time, sleep

import yagmail
import boto3
from botocore.exceptions import ClientError

from fastapi import Request, APIRouter
from fastapi.logger import logger
from fastapi.background import BackgroundTasks
from common._config import KAKAO_KEY, EMAIL_ADDR, EMAIL_PW
from errors import exceptions as ex
from models import KakaoMsgBody, MessageOk, SendEmail


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


email_content = """
<div style='margin-top:0cm;margin-right:0cm;margin-bottom:10.0pt;margin-left:0cm;line-height:115%;font-size:15px;font-family:"Calibri",sans-serif;border:none;border-bottom:solid #EEEEEE 1.0pt;padding:0cm 0cm 6.0pt 0cm;background:white;'>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:115%;font-size:15px;font-family:"Calibri",sans-serif;background:white;border:none;padding:0cm;'><span style='font-size:25px;font-family:"Helvetica Neue";color:#11171D;'>{}님! Aristoxeni ingenium consumptum videmus in musicis?</span></p>
</div>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:17.25pt;font-size:15px;font-family:"Calibri",sans-serif;background:white;vertical-align:baseline;'><span style='font-size:14px;font-family:"Helvetica Neue";color:#11171D;'>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Quid nunc honeste dicit? Tum Torquatus: Prorsus, inquit, assentior; Duo Reges: constructio interrete. Iam in altera philosophiae parte. Sed haec omittamus; Haec para/doca illi, nos admirabilia dicamus. Nihil sane.</span></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:10.0pt;margin-left:0cm;line-height:normal;font-size:15px;font-family:"Calibri",sans-serif;background:white;'><strong><span style='font-size:24px;font-family:"Helvetica Neue";color:#11171D;'>Expressa vero in iis aetatibus, quae iam confirmatae sunt.</span></strong></p>

<p style='margin-top:0cm;margin-right:0cm;margin-bottom:11.25pt;margin-left:0cm;line-height:17.25pt;font-size:15px;font-family:"Calibri",sans-serif;background:white;vertical-align:baseline;'><span style='font-size:14px;font-family:"Helvetica Neue";color:#11171D;'>Sit sane ista voluptas. Non quam nostram quidem, inquit Pomponius iocans; An tu me de L. Sed haec omittamus; Cave putes quicquam esse verius.&nbsp;</span></p>

<p>
<br>
</p>
"""


@router.post("email/send_by_gmail")
async def email_by_gmail(request: Request, mailing_list: SendEmail):
    send_email(mailing_list=mailing_list.email_to)
    return MessageOk()

# rest 서비스는 백그라운드로 빼서 작업을 시행해야함
# django celery
# fastapi background_tasks < 유저의 커넥션이 지속되지 않아도 되는 경우에 스레드 백그라운드 실행
# 많은 리소스를 필요로 하지만, 빠르고 많은 트래픽을 받을 수 있는 서비스 구축 가능

@router.post("email/send_by_gmail_on_bg")
async def send_by_gmail_on_bg(request: Request, mailing_list: SendEmail, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        send_email, mailing_list=mailing_list.email_to
    )
    return MessageOk()


def send_email(**kwargs):
    mailing_list = kwargs.get("mailing_list", None)
    email_pw = os.environ.get("EMAIL_PW", EMAIL_PW)
    email_addr = os.environ.get("EMAIL_ADDR", EMAIL_ADDR)
    last_email = ""
    if mailing_list:
        try:
            yag = yagmail.SMTP({email_addr: "KimJongkwang"}, email_pw)  # yet anoter email
            for m_l in mailing_list:
                contents = [
                    email_content.format(m_l.name)
                ]
                sleep(1)
                yag.send(m_l.email, 'Gmail 전송 테스트입니다.', contents)
                last_email = m_l.email
            return True
        except Exception as e:
            print(e)
            print(last_email)


@router.post("email/send_by_ses")
async def email_by_ses():
    sender = "Jk =?UTF-8?B?65287J207Ja4?= <sender@d9.is>"
    recipient = ["kjk6646@gmail.com"]
    # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
    region = "ap-northeast-2"

    # The subject line for the email.
    title = "안녕하세요! 테스트 이메일 입니다."

    # The email body for recipients with non-HTML email clients.
    BODY_TEXT = ("안녕하세요! Jk 입니다.\r\n"
                 "HTML 버전만 지원합니다!"
                 )

    # The HTML body of the email.
    BODY_HTML = """<html>
    <head></head>
    <body>
      <h1>안녕하세요! 반갑습니다.</h1>
      <p>기업에서 대규모 이메일 솔루션을 구축한다는 것은 복잡하고 비용이 많이 드는 작업이 될 수 있습니다. 이를 위해서는 인프라를 구축하고, 네트워크를 구성하고, IP 주소를 준비하고, 발신자 평판을 보호해야 합니다. 타사 이메일 솔루션 대부분이 상당한 규모의 선수금을 요구하고 계약 협상을 진행해야 합니다.
Amazon SES는 이러한 부담이 없으므로 몇 분 만에 이메일 발송을 시작할 수 있습니다. Amazon.com이 대규모의 자사 고객 기반을 지원하기 위해 구축한 정교한 이메일 인프라와 오랜 경험을 활용할 수 있습니다.</p>
    </body>
    </html>
                """

    # The character encoding for the email.
    charset = "UTF-8"

    # Create a new SES resource and specify a region.
    client = boto3.client(
        'ses',
        region_name=region,
        aws_access_key_id=os.environ.get("AWS_KEY", None),
        aws_secret_access_key=os.environ.get("AWS_SECRET", None),
    )

    # Try to send the email.
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': recipient
            },
            Message={
                'Body': {
                    'Html': {
                        'Charset': charset,
                        'Data': BODY_HTML,
                    },
                    'Text': {
                        'Charset': charset,
                        'Data': BODY_TEXT,
                    },
                },
                'Subject': {
                    'Charset': charset,
                    'Data': title,
                },
            },
            Source=sender,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

    return MessageOk()
