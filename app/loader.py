from os import getenv
from dotenv import load_dotenv
from pathlib import Path
from pydantic import BaseModel

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"


def load_prompt(prompt_name: str) -> str:
    prompt_path = PROMPTS_DIR / prompt_name
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found at: {prompt_path}")
    return prompt_path.read_text(encoding="utf-8")

class APIKey(BaseModel):
    openai_key: str

def load_api_key() -> APIKey:
    return APIKey(
        openai_key=getenv("OPENAI_KEY")
    )

class DataBaseConfig(BaseModel):
    host: str
    dbname: str
    user: str
    password: str
    port: int

def load_database() -> DataBaseConfig:
    return DataBaseConfig(
        host = getenv("host"),
        dbname = getenv("dbname"),
        user = getenv("user"),
        password = getenv("password"),
        port = int(getenv("port")),
    )