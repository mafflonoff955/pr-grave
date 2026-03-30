from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    GITHUB_TOKEN: str = ""
    PORT: int = 3001
    BASE_URL: str = "https://api.github.com"
    API_VERSION: str = "2022-11-28"
    CACHE_TTL_SECONDS: int = 300
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]

    @property
    def token_configured(self) -> bool:
        return bool(self.GITHUB_TOKEN)


settings = Settings()