import asyncio

from abc import ABC, abstractmethod
from pathlib import Path

from app.crop_image import crop_products
from app.gpt import Extractor
from app.parsers.base_parser import BaseParser
from app.utils import encode_image_to_base64, setup_flyer_dirs, get_safe_filename, save_to_json

from app.database import Database

class BasePipeline(ABC):
    def __init__(self, extractor: Extractor, database: Database, concurrency: int = 5):
        self.extractor = extractor
        self.database = database
        self.sem = asyncio.Semaphore(concurrency)

    @abstractmethod
    def get_store_name(self) -> str:
        pass

    @abstractmethod
    def get_parser(self) -> BaseParser:
        pass

    async def _process_single_image(self, image_path: Path) -> dict | None:
        try:
            async with self.sem:
                encode_image = encode_image_to_base64(str(image_path))
                result = await self.extractor.get_json_from_image_async(encode_image, self.get_store_name())
                return result
        except Exception as e:
            return None

    async def process_flyer(self, link: str) -> None:
        parser = self.get_parser()

        dirs = setup_flyer_dirs(self.get_store_name(), link)

        images_paths = parser.download_flyer(link, dirs["raw"])
        tasks = []

        for image_path in images_paths[:2]:  # 2 для теста
            task = self._process_single_image(image_path)
            tasks.append(task)

        promotions_json = await asyncio.gather(*tasks)

        for page_index, page in enumerate(promotions_json):
            page_folder_name = images_paths[page_index].stem
            for promo_index, promo in enumerate(page["promotions"]):
                safe_name = get_safe_filename(promo["product_name"])
                filename = f"{promo_index:03d}_{safe_name}.png"
                full_crop_path = dirs["crops"] / page_folder_name / filename
                promo["crop_path"] = str(full_crop_path)
                promo["source_image"] = str(images_paths[page_index])

            crop_products(images_paths[page_index], promotions_json[page_index]["promotions"])
        print(f"DEBUG: 📊 Итого валидных страниц для БД: {len(promotions_json)}")

        self.database.save_promotions_bulk(promotions_json, self.get_store_name())
        self.database.update_promotion_statuses()
        save_to_json(promotions_json, dirs["json"])

    async def run(self) -> None:
        links = self.get_parser().get_all_flyers()
        for link in links[:1]:  # тест
            await self.process_flyer(link)
