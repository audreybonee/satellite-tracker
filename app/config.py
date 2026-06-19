from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()


class Settings:
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./satellite_tracker.db")
    project_root: Path = Path(__file__).resolve().parents[1]


@lru_cache
def get_settings() -> Settings:
    return Settings()
