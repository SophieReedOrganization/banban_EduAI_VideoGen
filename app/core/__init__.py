from .config import Config
from .logger import Logger
from .mongodb import MongoDBClient

MongoDB = MongoDBClient()

async def initialize_mongodb():
    await MongoDB.initialize()

__all__ = ["Config", "Logger", "MongoDB", "initialize_mongodb"]
