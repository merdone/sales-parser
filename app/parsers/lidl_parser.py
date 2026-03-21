from playwright.async_api import async_playwright

from app.parsers.base_parser import BaseParser

class LidlParser(BaseParser):
    def get_basic_url(self) -> str:
        return "https://www.lidl.pl/c/nasze-gazetki/s10008614"

    async def get_all_flyers(self) -> list:
        links = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(self.get_basic_url())

            await page.wait_for_selector("div.leaflets-overview__content div.subcategory")

            elements = await page.locator("div.leaflets-overview__content div.subcategory a.flyer").all()

            for element in elements:
                link = await element.get_attribute("href")
                if link:
                    links.append(link)

            await context.close()
            await browser.close()

        return links

    async def get_pictures(self, url: str) -> list:
        pics = []
        max_pages = 100
        empty_retries = 0

        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(url)

            try:
                await page.locator("#onetrust-accept-btn-handler").click(timeout=20000)
                await page.wait_for_timeout(1000)
            except TimeoutError:
                pass

            await page.wait_for_timeout(3000)

            for _ in range(max_pages):
                imgs = await page.locator("img").all()
                new_pics_found = False

                for img in imgs:
                    src = await img.get_attribute("src")

                    if src and not src.startswith("data:image"):
                        if src not in pics:
                            pics.append(src)
                            new_pics_found = True

                if not new_pics_found:
                    empty_retries += 1
                    if empty_retries > 3:
                        break
                else:
                    empty_retries = 0

                await page.keyboard.press("ArrowRight")

                await page.wait_for_timeout(1500)

            await context.close()
            await browser.close()

        return pics[1:]