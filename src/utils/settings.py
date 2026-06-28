from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DB_CONNECTION: str
    TEST_DB_CONNECTION: str
    SECRET_KEY: str
    ALGORITHM: str
    EXP_MINUTES: int

settings = Settings()

print(settings.DB_CONNECTION)