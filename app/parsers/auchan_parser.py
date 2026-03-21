from pathlib import Path

from playwright.async_api import TimeoutError
from playwright.async_api import async_playwright

from app.parsers.base_parser import BaseParser

#TODO продумать фишку с определением "базовой" даты для Ашана и Карефура, а возможно и для всех, только в бедренке ничего не ставить

class AuchanParser(BaseParser):
    def get_basic_url(self) -> str:
        return "https://www.auchan.pl/pl/gazetki"

    async def get_all_flyers(self) -> list:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})

            page = await context.new_page()
            await page.goto(self.get_basic_url())

            try:
                await page.locator("id=onetrust-accept-btn-handler").click(timeout=1000)
            except TimeoutError:
                pass

            await page.wait_for_selector(".v-data-iterator")
            all_flyers = await page.locator(".v-data-iterator .row.justify-center > div").all()
            all_links = []

            for flyer in all_flyers:
                link = "https://www.auchan.pl" + await flyer.locator("a").get_attribute("href")
                all_links.append(link)

            await context.close()
            await browser.close()

        return all_links

    async def get_pictures(self, url: str) -> list:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(url)

            try:
                await page.get_by_role("button", name="Kontynuuj bez akceptacji").click()
                await page.get_by_role("button", name="Tak").click()
            except TimeoutError:
                pass

            for _ in range(50):
                try:
                    await page.locator("button:nth-child(4)").first.click(timeout=1000)
                except Exception:
                    break

            all_pictures = await page.locator(".image-map-container").all()
            all_links = []

            for picture in all_pictures:
                link = await picture.locator("img.back").get_attribute("src")
                all_links.append(link)

            await context.close()
            await browser.close()

        return all_links

    async def download_flyer(self, flyer_link: str, output_dir: Path) -> list[Path]:
        list_of_pictures = await self.get_pictures(flyer_link)
        saved_files = []
        for idx, img_url in enumerate(list_of_pictures):
            filename = f"{idx:03d}.png"
            full_path = output_dir / filename
            self.save_image(img_url, full_path)
            saved_files.append(full_path)
        return saved_files