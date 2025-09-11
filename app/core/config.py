import os
import sys
from pydantic_settings import BaseSettings


BASE_DIR = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(__file__)

ENV_PATH = os.path.join(BASE_DIR, ".env")

DB_PATH = os.path.join(BASE_DIR, "test.db")

DATABASE_URL_FROZEN = f"sqlite:///{DB_PATH}"
print(DATABASE_URL_FROZEN)


class Settings(BaseSettings):
    DATABASE_URL: str = DATABASE_URL_FROZEN
    EXPIRE_TOKEN_MINUTES: int = 20
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    LOGIN_ATTEMPTS: int = 3

    class Config:
        env_file = ENV_PATH


settings = Settings()
