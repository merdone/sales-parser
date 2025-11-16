from openai import OpenAI
from pydantic import BaseModel
import instructor
from typing import Optional, List

from utils import *


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


def get_json_from_text(ocr_content):
    key = load_api_key("open_ai")

    client = instructor.from_openai(OpenAI(api_key=key))

    system_prompt = load_prompt("ocr")

    response = client.chat.completions.create(
        model="gpt-5-mini",
        response_model=PromotionsList,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ocr_content}
        ],
    )

    return response.model_dump()


def get_json_from_image(image_base64):
    key = load_api_key("open_ai")

    client = instructor.from_openai(OpenAI(api_key=key))

    system_prompt = load_prompt("image")

    response = client.chat.completions.create(
        model="gpt-5-mini",
        response_model=PromotionsList,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            }}
        ],
    )

    return response.model_dump()
