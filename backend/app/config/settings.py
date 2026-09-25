from pathlib import Path
from urllib.parse import urlparse

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    groq_api_key: str
    groq_base_url: str = "https://api.groq.com/openai/v1"

    groq_model: str = "openai/gpt-oss-120b"
    groq_vision_model: str = "qwen/qwen3.6-27b"

    demo_app_url: str = "http://localhost:5173"

    backend_host: str = "127.0.0.1"
    backend_port: int = 8000

    max_agent_steps: int = 20
    agent_timeout_seconds: int = 120

    artifacts_dir: str = "artifacts"
    evidence_dir: str = "evidence"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def demo_app_domain(self) -> str:
        return urlparse(self.demo_app_url).hostname or ""


settings = Settings()
