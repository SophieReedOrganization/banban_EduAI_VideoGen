from google import genai
from google.cloud import storage
from functools import lru_cache
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

class _Config:
    
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.environ.get("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    APP_NAME: str = os.environ.get("APP_NAME", "k12-edu-ai-media-generator-gpu")
    APP_ENV: str = os.environ.get("APP_ENV", "dev")
    APP_VERSION: str = os.environ.get("APP_VERSION", "0.0.7")
    PROJECT_NUMBER: str = os.environ.get("PROJECT_NUMBER", "980700405323")
    REGION: str = os.environ.get("REGION", "asia-southeast1")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "api_2fK9mP4vL2nXhJ4qR8wY5cF3zB7xN9")
    ALGORITHM: str = os.environ.get("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    MONGODB_URI: Optional[str] = os.environ.get("MONGODB_URI", "mongodb+srv://lisa:XpK0m7TsMpdfnd4R@cluster-development.ud89k.mongodb.net/?retryWrites=true&w=majority&appName=cluster-development")
    MONGODB_DATABASE: Optional[str] = os.environ.get("MONGODB_DATABASE", "MediaStorage")
    GOOGLE_SA_CREDENTIALS_PATH: str = os.environ.get("GOOGLE_SA_CREDENTIALS_PATH", "./app/core/credentials/google.json")
    GOOGLE_OAUTH_CREDENTIALS_PATH: str = os.environ.get("GOOGLE_OAUTH_CREDENTIALS_PATH", "./app/core/credentials/oauth.json")
    BASE_URL: str = os.environ.get("BASE_URL", "http://localhost:8000")
    
    def setup_environment(self):
        if not os.path.exists(self.GOOGLE_SA_CREDENTIALS_PATH):
            raise FileNotFoundError(f"Can't find Google credentials file: {self.GOOGLE_SA_CREDENTIALS_PATH}")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.GOOGLE_SA_CREDENTIALS_PATH
    
    def setup_ai_models(self):
        self.vertex_client = genai.Client(vertexai=True, project='oneclasscomputex', location='us-central1')
        self.vertex_model = "gemini-2.0-flash-001"
    
    def setup_storage_clients(self):
        self.google_storage_client = storage.Client()
        self.gcs_generate_bucket = self.google_storage_client.bucket("generate_educational_video")

@lru_cache()
def get_config_instance():
    config = _Config()
    config.setup_environment()
    config.setup_ai_models()
    config.setup_storage_clients()
    return config

Config = get_config_instance()