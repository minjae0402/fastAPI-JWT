import os
from dotenv import load_dotenv
from pydantic import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    google_client_id: str
    google_client_secret: str
    naver_client_id: str
    naver_client_secret: str
    authjwt_secret_key: str

    class Config:
        env_file = ".env"

settings = Settings()
