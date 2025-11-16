from openai import OpenAI
from pydantic import BaseModel
import instructor
from typing import Optional, List
import os
import json
from dotenv import load_dotenv


class Promotion(BaseModel):
    product_name: str
    weight: Optional[str] = None
    date: str
    start_date: str
    end_date: str
    new_price: Optional[float] = None
    old_price: Optional[float] = None
    new_price_per_kg: Optional[float] = None
    old_price_per_kg: Optional[float] = None
    promotion: str
    category: str


class PromotionsList(BaseModel):
    promotions: List[Promotion]


def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def get_json_from_text(ocr_content):
    load_dotenv()

    key = os.getenv("OPENAI_KEY")

    client = instructor.from_openai(OpenAI(
        api_key=key))

    SYSTEM_PROMPT = load_prompt("prompts/system_prompt.txt")

    response = client.chat.completions.create(
        model="gpt-5-mini",
        response_model=PromotionsList,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": ocr_content}
        ],
    )

    with open("promotions.json", "w", encoding="utf-8") as file:
        json.dump(
            response.model_dump(),
            file,
            ensure_ascii=False,
            indent=2
        )
