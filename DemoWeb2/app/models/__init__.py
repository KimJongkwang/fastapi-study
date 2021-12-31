from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine

from app.config.config import get_secrets


class MongoDB:
    def __init__(self):
        self.client = None
        self.engine = None

    def connect(self):
        self.client = AsyncIOMotorClient(get_secrets("MONGO_URL"))
        self.engine = AIOEngine(
            motor_client=self.client, database=get_secrets("MONGO_DB_NAME")
        )
        print("Success Connecting Database {0}".format(get_secrets("MONGO_DB_NAME")))

    def close(self):
        self.engine.close()
        print("Unconnecting Database")


mongodb = MongoDB()
