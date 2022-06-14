# FastAPI 연습해보자

[공식 도큐먼트](https://fastapi.tiangolo.com/)

## 1. Tutorial 01 (시작)

- 설치: `$pip install fastapi`
- AGSI 서버 설치: `$pip install uvicorn` | `$pip install hypercorn`
- 실행: `$uvicorn main:app --reload --host=0.0.0.0 --port=8000

  - main: main.py
  - app: app=FastAPI()
  - --reload: 코드 변경시 자동 저장 및 시작
  - --host: 호스트주소
  - --port: 포트

- Swagger
  - FastAPI는 Swagger를 제공합니다.
  - 8000/docs: 작성한 API 문서 제공
  - 8000/redocs: OpenAPI 명세서와 같은 페이지 제공

#### 테스트 코드

`test_request.py` 실행시 10초 간격 get, post 응답 출력

## 2. Noti-api
