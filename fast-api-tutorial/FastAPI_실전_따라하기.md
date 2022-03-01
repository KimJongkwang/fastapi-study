코딩알려주는 라이언님 유튜브를 참고하여 작성

1장 FastAPI 맛보기
2장 프로젝트 구조

1. main.py

- 프로젝트 run (create_app)

2. models.py

- Web을 통해 받는 JSON을 객체화하기 위한 모델
- pydantic을 통해 validation

2. common

- config.py:

  - 환경설정(로컬 - 개발or운영)
  - DB initalize
    - mysql 서버 정보

- consts.py
  - 고정값 저장(JWT 토큰 secret)
  - db정보는 로컬, 운영에 따라 달라지므로 config
  - 참조할 상대경로 등을 들수 있겠음

3. database

- conn.py:
  - SQLAlchemy
    - MySQL to ORM
    - init app 설정,
- schema.py:
  - table 스키마

5. routes

- main.py 에서 app.include_router()으로 정의할 endpoint(router)
- index.py
  - root "/"
- auth.py
  - 계정 생성, 로그인 및 사용자 인증 등

3장 FastAPI에서 데이터베이스 연결하기( SQLAlchemy)

- docker mysql 설치

  - 1. pull image
    - docker pull mysql:8.0.17
  - 2. docker run
    - docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=패스워드 --name docker-mysql -v /Users/dingrr/mysqldb:/var/lib/mysql mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    - # 3306포트, 패스워드, volume 설정(/Users/dingrr/mysqldb --> E드라이브가 2TB로 남길래 E드라이브로 변경해줌) , 뒤는 encoding
    - docker run -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=rlawhdrhkd2! --name docker-mysql -v E:\docker-container\DockerDesktop\mysql:/var/lib/mysql mysql --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
  - 3. 설치 및 실행 확인
    - docker ps(현재 실행, -a 모든 컨테이너)
    - docker exec -it docker-mysql bash (컨테이너 내 bash 실행)
    - docker stop {컨테이너 명} : 컨테이너 중지
    - docker start {컨테이너 명} : 중지된 컨테이너 실행
  - 4.  유저계정 생성

    - travis CI를 사용할 계획으로 MySQL traivs 유저 생성
      - CREATE USER '아이디'@'%' IDENTIFIED BY '비밀번호'; 입력하기
      - CREATE USER 'travis'@'%' IDENTIFIED BY '0000';
      - '%'로써 외부 host 접근 권한
    - 당장은 부여하지 않고 추후에 필요시 필요 권한만 부여(권한 부여)
      - 모든 권한
      - GRANT ALL PRIVILEGES ON _._ TO 계정ID@localhost IDENTIFIED BY '비밀번호';
      - 특정 DB 권한
      - GRANT ALL PRIVILEGES ON DB이름.\* TO 계정ID@localhost IDENTIFIED BY '비밀번호';
      - 외부 host에서 특정 DB 권한
      - GRANT ALL PRIVILEGES ON DB이름.\* TO 계정ID@'%' IDENTIFIED BY '비밀번호';
    - 계정생성 및 권한 부여 반영
      - FLUSH PRIVILEGES;
    - 혹시 모를 계정삭제 커맨드

      - DROP USER 'user'@localhost;

    - 4-1) DBeaver 연결
      - mysql 연결시 Public Key Retrieval is not allowed 에러 발생
      - mysql 8.x 이후부터 Public Key Retrieval 설정이 필요
      - 연결환경에서 Driver properties의 allowPublicKeyRetrieval를 True로 설정
    - 4-2) travis 계정 연결

      - 도커에서 DB 구성시 localhost, '%' 등 호스트에서 연결이 안되는 에러발생
      - --> 유저 생성시 travis@'172.17.0.1' 도커 로컬호스트 ip로 계정 생성 해결
      - 이때, 모종의 이유로 root로 drop이나 grant 명령어가 먹히지 않는다면, 'root'@'%' 계정 생성 및 권한 부여(외부 접근허용) 다만, 권한작업 이후 바로 drop 필요

        <!-- docker-compose로도 추가 가능
        version: "3" # 파일 규격 버전
        services: # 이 항목 밑에 실행하려는 컨테이너 들을 정의
          db: # 서비스 명
            image: mysql # 사용할 이미지
            container_name: custom_mysql # 컨테이너 이름 설정
            ports:
              - "3306:3306" # 접근 포트 설정 (컨테이너 외부:컨테이너 내부)
            environment: # -e 옵션
              MYSQL_ROOT_PASSWORD: "password"  # MYSQL 패스워드 설정 옵션
            command: # 명령어 실행
              - --character-set-server=utf8mb4
              - --collation-server=utf8mb4_unicode_ci
            volumes:
              - /Users/jmlim/datadir:/var/lib/mysql # -v 옵션 (다렉토리 마운트 설정) -->

4장 FastAPI에서 회원가입 만들기! Pydantic을 이용한 Validation

- 1. 회원가입 router 생성

  - auth.py
    - 회원계정 생성, crud
    - 토큰 발행 pip install pyjwt(Json Web Token 발행)
    - bcrypt 설치
    - 회원가입(register)
      - 유저가 회원가입함. 데이터 서버로 전송(POST)
      - sns_type, email, pw 등 json 받아 email 무결성 확인 후 패스워드 hashing, 유저 DB 등록(현재 email만 가능, sns 미구현)
      - 이후 JWT 토큰 발행(pw db 저장)

- 2. swagger를 통해 validaion 테스트
  - localhost/docs 접근
  - endpoint 별 post execute로 테스트

5장 FastAPI 미들웨어 생성, 사용 및 삽질을 피하기 위한 방법

- middlewares
  - trusted_hosts.py
    - 기존 starlette에 있는 미들웨어 TrustedHostMiddleware를 커스텀.
    - 등록된 호스트 url을 검사해줌.
    - trust hosts는 개발환경인지, 운영환경인지에 따라 config에서 관리
    - except_path 추가. 검사 제외 url
  -
