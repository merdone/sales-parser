from playwright.async_api import async_playwright

from app.parsers.base_parser import BaseParser

class BiedronkaParser(BaseParser):
    def get_basic_url(self):
        return "https://www.biedronka.pl/pl/gazetki"

    async def get_all_flyers(self) -> list:
        links = []
        forbidden_words = ("home", "zakupy", "piwniczka", "book", "strona-gazetki", "glovo")

        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(self.get_basic_url())

            await page.wait_for_selector("div.slot a.page-slot-columns")

            all_link_elements = await page.locator("div.slot a.page-slot-columns").all()

            for element in all_link_elements:
                link = await element.get_attribute("href")

                if link and all(word not in link for word in forbidden_words):
                    links.append(link)

            await context.close()
            await browser.close()

        return links

    async def extract_real_urls(self, current_slide):
        valid_urls = []
        imgs = await current_slide.locator("img").all()
        for img in imgs:
            src = await img.get_attribute("src")
            if src and not src.startswith("data:image"):
                valid_urls.append(src)
        return valid_urls

    async def get_pictures(self, url: str) -> list:
        pics = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch()
            context = await browser.new_context(viewport={"width": 1920, "height": 1080})
            page = await context.new_page()

            await page.goto(url)

            try:
                await page.locator("#onetrust-accept-btn-handler").click(timeout=2000)
            except TimeoutError:
                pass

            gallery = page.locator("#gallery-leaflet")
            slides = gallery.locator("div.embla__slide")

            await slides.first.wait_for(state="attached")
            slides_count = await slides.count()

            nav_buttons = gallery.locator(
                "button.inline-flex.items-center.justify-center.gap-2.whitespace-nowrap.rounded-md.text-sm.font-medium.transition-colors")


            for i in range(slides_count):
                slide = slides.nth(i)

                urls = await self.extract_real_urls(slide)

                if not urls:
                    await slide.scroll_into_view_if_needed()
                    await page.wait_for_timeout(500)
                    urls = await self.extract_real_urls(slide)

                pics.extend(urls)

                if i < slides_count - 1:
                    btn_count = await nav_buttons.count()
                    if btn_count > 0:
                        next_btn = nav_buttons.nth(1) if btn_count > 1 else nav_buttons.last
                        await next_btn.click(force=True)
                        await page.wait_for_timeout(400)

            await context.close()
            await browser.close()

        return pics