from app.parsers.auchan_parser import AuchanParser
from app.pipelines.base_pipeline import BasePipeline

import asyncio

from app.services.image_processing import crop_products
from app.parsers.base_parser import BaseParser
from app.services.utils import setup_flyer_dirs, get_safe_filename, save_to_json

class AuchanPipeLine(BasePipeline):
    def _get_store_name(self) -> str:
        return "auchan"

    def _get_parser(self) -> BaseParser:
        return AuchanParser()

    async def run(self) -> None:
        links = await self._get_parser().get_all_flyers()
        for link in links[:self.link_limit]:
            await self.process_flyer(link)

    async def process_flyer(self, link: str) -> None:
        parser = self._get_parser()

        dirs = setup_flyer_dirs(self._get_store_name(), link)
        images_paths = await parser.download_flyer(link, dirs["raw"])
        tasks = []
        for image_path in images_paths[:self.page_limit]:
            task = self._process_single_image(image_path)
            tasks.append(task)

        promotions_json = await asyncio.gather(*tasks)
        for page_index, page in enumerate(promotions_json):
            page_folder_name = images_paths[page_index].stem
            try:
                for promo_index, promo in enumerate(page["promotions"]):
                    safe_name = get_safe_filename(promo["product_name"])
                    filename = f"{promo_index:03d}_{safe_name}.png"
                    full_crop_path = dirs["crops"] / page_folder_name / filename
                    promo["crop_path"] = str(full_crop_path)
                    promo["source_image"] = str(images_paths[page_index])
            except Exception:
                pass
            try:
                crop_products(images_paths[page_index], promotions_json[page_index]["promotions"])
            except Exception:
                pass

        self.database.save_promotions_bulk(promotions_json, self._get_store_name())
        self.database.update_promotion_statuses()
        jsons_paths = save_to_json(promotions_json, dirs["json"])