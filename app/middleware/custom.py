from app.core import Logger
from datetime import datetime
from json import JSONEncoder
from fastapi.responses import JSONResponse
from fastapi import Request
from typing import Any
from bson import ObjectId
import time, psutil

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(obj, ObjectId):
            return str(obj)
        elif isinstance(obj, (list, tuple)):
            return [self.default(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self.default(value) for key, value in obj.items()}
        return super().default(obj)

class CustomJSONResponse(JSONResponse):
    def render(self, content: Any) -> bytes:
        return CustomJSONEncoder().encode(content).encode("utf-8")

async def performance_monitoring_middleware(request: Request, call_next):
        process = psutil.Process()
        start_time = time.time()
        memory_before = process.memory_info().rss
        response = await call_next(request)
        memory_after = process.memory_info().rss
        process_time = time.time() - start_time
        memory_used = memory_after - memory_before
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Memory-Used"] = str(memory_used / 1024 / 1024)
        Logger.debug(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")
        return response