from dotenv import load_dotenv

load_dotenv()

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "dev"
    BASE_URL: str = "http://localhost:5173"

    # Database Configuration
    CONNECTION_STRING: str = ""

    # Local database settings
    DB_USER: str = "stash"
    DB_PASSWORD: str = "stash123"
    DB_HOST: str = "localhost"
    DB_PORT: str = "5432"
    DB_NAME: str = "stash"

    # Security
    JWT_SECRET: str = "super_secret_change_me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 30

    # AI
    OPENAI_API_KEY: str = ""
    MAX_CONTENT_LENGTH: int = 4000

    # Email settings
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = "stash@example.com"

    # Admin settings
    ADMIN_API_KEY: str = "change_me_in_production"

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


# Create settings instance
settings = Settings()
