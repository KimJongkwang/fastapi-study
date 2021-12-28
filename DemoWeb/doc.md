# DB 연결

1. 시크릿 변수 설정

- API KEY, DB 정보 등의 비공개 정보들에 대해 `secrets.json`와 같은 json에 저장
- `config.py` 에서 get_secret()을 정의하여 json을 읽어 KEY, DB 정보를 불러옴

2. `odmantic`을 사용하여 fastapi와 연결

- odmantic은 ODM(Object-Document Mapper) pydantic을 통해 정의한 모델을 nosql을 객체로 처리할 수 있도록 도와줌
- odmantic과 대조적으로 RDBMS를 사용할 경우 ORM(Object-Relational Mapper) sqlalchemy가 대표적

<!-- github token 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 -->
