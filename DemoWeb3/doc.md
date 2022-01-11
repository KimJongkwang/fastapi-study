# 콜렉터스 북북이 데모 개발

1. 프로젝트 세팅

- UI
  - 템플릿 구성
  - 템플릿별 request/response 테스트
    - `app.get("/", reponse_class=HTMLResponse)` # get으로 데이터 요청반환시, response 클래스를 설정할 수 있음 Defalut는 JsonResponse
    - 템플릿 구성
      - `from fastapi.templating import Jinja2Templates`
      - `templates = Jinja2Templates("{템플릿 폴더}")`
      - HTML로 보낼시 반환객체는 아래와 같음
        - `templates.TemplateResponse("{템플릿 명}", {"request": request, .. 반환 데이터)`

2. DB 연결

- 시크릿 변수 설정

  - API KEY, DB 정보 등의 비공개 정보들에 대해 `secrets.json`와 같은 json에 저장
  - `config.py` 에서 get_secret()을 정의하여 json을 읽어 KEY, DB 정보를 불러옴

- `odmantic`을 사용하여 fastapi와 연결
  <!-- - odmantic은 ODM(Object-Document Mapper) pydantic을 통해 정의한 모델을 nosql을 객체로 처리할 수 있도록 도와줌
  - odmantic과 대조적으로 RDBMS를 사용할 경우 ORM(Object-Relational Mapper) sqlalchemy가 대표적
  https://art049.github.io/odmantic/engine/ -->
  - `main.py`의 app.on_event()을 통해서 서버 실행 및 종료시 DB 연결 이벤트 추가
  - `models.__init__.py` DB 연결, 해제 정의

<!-- github token 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 -->

3. 기능구현

- 요구사항
  - 버튼 클릭시 네이버 책 검색 API 결과
  - 책 이미지, 책 제목, 책 출판사, 가격 정보 제공
- 기능정의

  - FUNC-001

    - 검색창 키워드 입력시 네이버 책 검색 API 해당 키워드로 request
    - 검색창 입력없을 경우 입력 "입력해주세요" 반환
    - 키워드 당 50개의 결과값 반환

  - FUNC-002
    - DB는 MongDB 저장
    - 검색한 키워드가 DB에 있을 경우 DB에서 조회하여 반환

4. 프로젝트 구성

- 프로젝트 구성
  - 폴더트리
    - DemoWeb3<br>
      ├ server.py <br> <!-- uvicorn 실행 -->
      └ app<br>
      　 ├ main.py<br> <!-- main logic 실행 -->
      　 ├ config <br>
      　 │ ├ secrets.json <br> <!-- api key, db info 등 -->
      　 │ └ config.py <br> <!-- return secrets -->
      　 ├ script <br> <!-- Book scraper logic -->
      　 │ ├ book_scraper.py
