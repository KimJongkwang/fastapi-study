# FastAPI Tutorial

1. Tutorial 01 (시작)
- 설치: `$pip install fastapi`
- AGSI 서버 설치: `$pip install uvicorn` | `$pip install hypercorn`
- 실행: `$uvicorn main:app --reload --host=0.0.0.0 --port:8000
    - main: main.py
    - app: app=FastAPI()
    - --reload: 코드 변경시 자동 저장 및 시작
    - --host: 호스트주소
    - --port: 포트