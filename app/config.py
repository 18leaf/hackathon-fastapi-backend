from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str
    MONGO_URI: str
    DATABASE_NAME: str
    GITHUB_TOKEN: str

    class Config:
        env_file = ".env"


settings = Settings()
