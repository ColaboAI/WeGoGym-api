from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_DIR = Path(__file__).parent.parent.parent


class AiConfig(BaseSettings):
    # AI SETTINGS
    OPENAI_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=f"{PROJECT_DIR}/.env.ai",
    )


@lru_cache()
def get_ai_config():
    return AiConfig()


ai_settings = get_ai_config()
