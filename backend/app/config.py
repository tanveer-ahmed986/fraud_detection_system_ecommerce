from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://fraud_user:fraud_pass@db:5432/fraud_db"
    database_url_sync: str = "postgresql://fraud_user:fraud_pass@db:5432/fraud_db"
    api_key: str = "change-me-in-production"
    rate_limit_per_second: int = 100
    model_dir: str = "models"
    fallback_amount_limit: float = 50.0
    fraud_threshold: float = 0.50
    log_level: str = "INFO"

    model_config = {"env_file": ".env"}


settings = Settings()
