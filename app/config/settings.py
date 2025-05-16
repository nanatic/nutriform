from pydantic_settings import BaseSettings
from pydantic import RedisDsn, PostgresDsn, Field


class Settings(BaseSettings):
    database_url: PostgresDsn
    redis_broker_url: RedisDsn = Field(..., alias='CELERY_BROKER_URL')
    redis_result_backend: RedisDsn = Field(..., alias='CELERY_RESULT_BACKEND')

    debug: bool = Field(False, alias='DEBUG')
    secret_key: str = Field(..., alias='SECRET_KEY')
    access_token_expire_minutes: int = Field(30, alias='ACCESS_TOKEN_EXPIRE_MINUTES')

    smtp_host: str = Field(..., alias='SMTP_HOST')
    smtp_port: int = Field(..., alias='SMTP_PORT')
    smtp_user: str = Field(..., alias='SMTP_USER')
    smtp_pass: str = Field(..., alias='SMTP_PASS')
    from_email: str = Field(..., alias='FROM_EMAIL')
    admin_email: str = Field(..., alias='ADMIN_EMAIL')

    celery_timezone: str = "UTC"
    class Config:
        env_file = ".env"
        extra = "forbid"  # запрещаем лишние переменные, чтобы ловить ошибки

def get_settings() -> Settings:
    return Settings()