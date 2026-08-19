"""Project configuration loaded from environment variables.

Project-specific defaults are embedded below so this folder runs immediately.
A local `.env` file can override any default without editing source code.
"""
from dataclasses import dataclass
import os
from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    project_name: str = os.getenv("PROJECT_NAME", 'Internet Services — Pricing and Revenue Optimization')
    industry: str = os.getenv("INDUSTRY", 'Internet Services')
    use_case: str = os.getenv("USE_CASE", 'Pricing and Revenue Optimization')
    task_type: str = os.getenv("TASK_TYPE", 'optimization')
    database_path: str = os.getenv("DATABASE_PATH", "data/app.db")
    use_ollama: bool = os.getenv("USE_OLLAMA", "false").lower() == "true"
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "granite3.2:latest")

settings = Settings()
