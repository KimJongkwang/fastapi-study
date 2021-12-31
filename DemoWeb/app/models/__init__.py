from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine
from app.config import MONGO_URL, MONGO_DB_NAME


class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        print("DB와 연결 중 입니다.")
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.engine = AIOEngine(motor_client=self.client, database=MONGO_DB_NAME)
        print("DB와 성공적으로 연결이 되었습니다.")

    def close(self):
        print("DB와의 연결을 끊는 중입니다.")
        self.client.close()
        print("DB와 성공적으로 연결이 해제 되었습니다.")


mongodb = MongoDB()
