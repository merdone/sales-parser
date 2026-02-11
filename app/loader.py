from os import getenv
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"

biedronka_url = str(getenv("biedronka_url"))


def load_prompt(prompt_name: str) -> str:
    prompt_path = PROMPTS_DIR / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found at: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")


def load_api_key() -> str:
    return getenv("OPENAI_KEY")


def load_database() -> dict:
    return {
        "host": getenv("host"),
        "dbname": getenv("dbname"),
        "user": getenv("user"),
        "password": getenv("password"),
        "port": getenv("port"),
    }
