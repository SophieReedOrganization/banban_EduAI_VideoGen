from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ReturnDocument
from app.core.config import Config
from app.core.logger import Logger
from typing import Dict, List

class MongoDBClient:
    instance = None
    init_flag = False
    
    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

    def __init__(self):
        if MongoDBClient.init_flag:
            return
        try:
            self.client = None
            MongoDBClient.init_flag = True
        except Exception as e:
            Logger.error(f"Error initializing MongoDB: {e}")
            raise
    
    async def initialize(self):
        """異步初始化連接"""
        if self.client is not None:
            return
        try:
            self.client = await self._create_connection(Config.MONGODB_URI)
            Logger.debug(f"MongoDB connected successfully.")
        except Exception as e:
            Logger.error(f"Error connecting to MongoDB: {e}.")
            raise

    async def _create_connection(self, uri: str) -> AsyncIOMotorClient:
        return AsyncIOMotorClient(uri, maxPoolSize=100, minPoolSize=10)

    async def _get_collection(self, collection: str, db_choice: str = "default"):
        try:
            db_mapping = {
                "default": self.client[Config.MONGODB_DATABASE],
            }
            selected_db = db_mapping.get(db_choice, self.client[Config.MONGODB_DATABASE])
            return selected_db[collection]
        except Exception as e:
            Logger.error(f"Error getting database: {e}")
            raise

    async def get_one(self, collection: str, query: Dict, db_choice: str = "default") -> Dict:
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.find_one(query)
    
    async def get_many(self, collection, pipeline, db_choice="default", timeout=30):
        collection_obj = await self._get_collection(collection, db_choice)
        cursor = collection_obj.aggregate(pipeline, maxTimeMS=timeout * 1000)
        return await cursor.to_list(length=None)

    async def insert_one(self, collection: str, document: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        result = await collection_obj.insert_one(document)
        return result

    async def insert_many(self, collection: str, documents: List[Dict], db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        result = await collection_obj.insert_many(documents)
        return result.inserted_ids

    async def update_one(self, collection: str, query: Dict, update: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.update_one(query, update, upsert=False)

    async def update_many(self, collection: str, query: Dict, update: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.update_many(query, update)

    async def upsert_one(self, collection: str, query: Dict, update: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.update_one(query, update, upsert=True)

    async def upsert_many(self, collection: str, operations: List[Dict], db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        from pymongo import UpdateOne
        formatted_operations = [
            UpdateOne(
                op['updateOne']['filter'],
                op['updateOne']['update'],
                upsert=op['updateOne'].get('upsert', False)
            )
            for op in operations
        ]
        return await collection_obj.bulk_write(formatted_operations)

    async def delete_one(self, collection: str, query: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.delete_one(query)

    async def delete_many(self, collection: str, query: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.delete_many(query)

    async def find_one_and_update(self, collection: str, query: Dict, update: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.find_one_and_update(query, update, return_document=ReturnDocument.AFTER)

    async def find_one_and_delete(self, collection: str, query: Dict, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.find_one_and_delete(query)

    async def delete_database(self, collection: str, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.delete_many({})

    async def count(self, collection: str, query: Dict = {}, db_choice: str = "default"):
        collection_obj = await self._get_collection(collection, db_choice)
        return await collection_obj.count_documents(query)

    async def list_collection_names(self, db_choice: str = "default") -> List[str]:
        """取得指定資料庫中所有集合的名稱"""
        try:
            db_mapping = {
                "default": self.client[Config.MONGODB_DATABASE],
            }
            selected_db = db_mapping.get(db_choice, self.client[Config.MONGODB_DATABASE])
            return await selected_db.list_collection_names()
        except Exception as e:
            Logger.error(f"Error listing collection names: {e}")
            raise 