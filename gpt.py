from openai import OpenAI
from openai import AsyncOpenAI

from pydantic import BaseModel
import instructor
from typing import Optional, List

from utils import timer, async_timer

from utils import load_api_key, load_prompt, encode_image_to_base64, save_to_json


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


@timer
def get_json_from_image(image_base64, system_prompt=None):
    if system_prompt is None:
        system_prompt = load_prompt()
    key = load_api_key()

    client = instructor.from_openai(OpenAI(api_key=key))

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


@timer
def json_from_image_interface(image_path: str, name: str, prompt = None):
    encode_image = encode_image_to_base64(image_path)
    promotions = get_json_from_image(encode_image, prompt)
    save_to_json(promotions, name)
    return promotions


@async_timer
async def get_json_from_image_async(image_base64: str) -> dict:
    key = load_api_key()

    async_client = AsyncOpenAI(api_key=key)
    client = instructor.from_openai(async_client)

    system_prompt = load_prompt()

    response = await client.chat.completions.create(
        model="gpt-5-mini",
        response_model=PromotionsList,
        messages=[
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{image_base64}"
                    }
                },
            },
        ],
    )

    return response.model_dump()


@async_timer
async def json_from_image_interface_async(image_path: str, name: str):
    encode_image = encode_image_to_base64(image_path)
    promotions = await get_json_from_image_async(encode_image)
    save_to_json(promotions, name)
    return promotions
