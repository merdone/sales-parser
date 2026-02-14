import asyncio
from app.gpt import Extractor
from app.parsers.biedronka_parser import BiedronkaParser
from app.utils import setup_flyer_dirs, encode_image_to_base64, save_to_json, get_safe_filename
from app.crop_image import crop_products


async def process_single_image(gpt, sem, image_path):
    async with sem:
        encode_image = encode_image_to_base64(str(image_path))
        result = await gpt.get_json_from_image_async(encode_image, "biedronka")
        return result


async def main():
    parser = BiedronkaParser()
    gpt = Extractor()
    sem = asyncio.Semaphore(5)
    flyer_links = parser.get_all_flyers()[:1]

    for link in flyer_links:
        dirs = setup_flyer_dirs("biedronka", link)

        images_paths = parser.download_flyer(link, dirs["raw"])
        tasks = []

        for image_path in images_paths[:2]:
            task = process_single_image(gpt, sem, image_path)
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

        json_paths = save_to_json(promotions_json, dirs["json"])

    await gpt.close()


if __name__ == '__main__':
    asyncio.run(main())