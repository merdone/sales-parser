from openai import AsyncOpenAI

from pydantic import BaseModel, conint
import instructor
from typing import Optional, List

from app.utils import async_timer
from app.loader import load_api_key, load_prompt
from app.utils import encode_image_to_base64, save_to_json

from typing import Dict


class MaskPoint(BaseModel):
    x: conint(ge=0, le=100)
    y: conint(ge=0, le=100)


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
    mask: List[MaskPoint]


class PromotionsList(BaseModel):
    promotions: List[Promotion]


class Extractor:
    def __init__(self, model_name: str = "gpt-5-mini"):
        self.api_key = load_api_key()
        self.model_name = model_name
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        self.client = instructor.from_openai(self.async_client)
        self._prompts_cache: Dict[str, str] = {}

    def _get_prompt_content(self, prompt_name: str) -> str:
        if prompt_name not in self._prompts_cache:
            self._prompts_cache[prompt_name] = load_prompt(prompt_name)
        return self._prompts_cache[prompt_name]

    @async_timer
    async def get_json_from_image_async(self, image_base64: str, store_name: str) -> dict:
        prompt_filename = f"{store_name}_prompt"
        system_prompt = self._get_prompt_content(prompt_filename)

        response = await self.client.chat.completions.create(
            model=self.model_name,
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
    async def json_from_image_interface_async(self, image_path: str, name: str):
        encode_image = encode_image_to_base64(image_path)
        promotions = await self.get_json_from_image_async(encode_image)
        save_to_json(promotions, name)
        return promotions

    async def close(self):
        await self.async_client.close()