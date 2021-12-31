# 콜렉터스 북북이 데모 개발

1. 프로젝트 세팅

- UI
  - 템플릿 구성
  - 템플릿별 request/response 테스트
- 프로젝트 구성
  - 폴더트리
    - DemoWeb2<br>
      ├ server.py <br> <!-- uvicorn 실행 -->
      └ app<br>
      　 ├ main.py<br> <!-- main 실행 -->
      　 ├ config <br>
      　 │ ├ secrets.json <br> <!-- api key, db info 등 -->
      　 │ └ config.py <br> <!-- return secrets -->
      　 ├ config <br>

2. DB 연결

- 시크릿 변수 설정

  - API KEY, DB 정보 등의 비공개 정보들에 대해 `secrets.json`와 같은 json에 저장
  - `config.py` 에서 get_secret()을 정의하여 json을 읽어 KEY, DB 정보를 불러옴

- `odmantic`을 사용하여 fastapi와 연결
  <!-- - odmantic은 ODM(Object-Document Mapper) pydantic을 통해 정의한 모델을 nosql을 객체로 처리할 수 있도록 도와줌
  - odmantic과 대조적으로 RDBMS를 사용할 경우 ORM(Object-Relational Mapper) sqlalchemy가 대표적 -->
  - `main.py`의 app.on_event()을 통해서 서버 실행 및 종료시 DB 연결 이벤트 추가
  - `models.__init__.py` DB 연결, 해제 정의

<!-- github token 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 -->
