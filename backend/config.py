from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    google_credentials_json: str = ""
    google_drive_folder_id: str = ""
    max_file_size_mb: int = 500
    upload_dir: str = "/tmp/meetbot_uploads"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
