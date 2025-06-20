from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core import Logger, Config, initialize_mongodb
from app.middleware import performance_monitoring_middleware
from datetime import datetime
from app.modules.video.router import router as video_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    Logger.info(f"Starting {Config.APP_NAME} service... {Config.APP_ENV}")
    await initialize_mongodb()
    yield
    Logger.info(f"Shutting down {Config.APP_NAME} service... {Config.APP_ENV}")

def apply_middlewares(app: FastAPI):
    app.middleware("http")(performance_monitoring_middleware)

def apply_configure_cors(app: FastAPI):
    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def apply_routes(app: FastAPI):
    @app.get("/", tags=["default"], summary="System Information", description="Get System Basic Information and Status")
    async def root():
        return {
            "service": Config.APP_NAME,
            "version": Config.APP_VERSION,
            "environment": Config.APP_ENV,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "documentation": "/docs",
            "openapi": "/openapi.json",
            "video": "/video"
        }
    app.include_router(video_router)

def create_app() -> FastAPI:
    
    tags_metadata = [
        {"name": "default", "description": "Default API"},
        {"name": "video", "description": "Generate Video API"}
    ]

    app = FastAPI(
        title=f"{Config.APP_NAME.replace('-', ' ').title()}",
        description=f"Running in {Config.APP_ENV} environment",
        lifespan=lifespan,
        version=f"{Config.APP_ENV}.{Config.APP_VERSION}",
        openapi_tags=tags_metadata
    )
    
    apply_configure_cors(app)
    apply_middlewares(app)
    app.add_event_handler("startup", lifespan(app).__aenter__)
    app.add_event_handler("shutdown", lifespan(app).__aexit__)
    apply_routes(app)

    return app

# 開發模式快速啟動
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:create_app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        factory=True
    )