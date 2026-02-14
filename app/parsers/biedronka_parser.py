import requests
from bs4 import BeautifulSoup
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from app.parsers.base_parser import BaseParser

class BiedronkaParser(BaseParser):
    def get_basic_url(self):
        return "https://www.biedronka.pl/pl/gazetki"

    def get_all_flyers(self) -> list:
        links = []
        r = requests.get(self.get_basic_url(), headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        print()
        for element in soup.find_all("div", {"class": "slot"}):
            link = element.find("a", {"class": "page-slot-columns"}).get("href")
            if all(word not in link for word in ("home", "zakupy", "piwniczka", "book", "strona-gazetki")):
                links.append(link)
        return links


    def get_pictures(self, url: str) -> None:
        driver = webdriver.Firefox()
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        try:
            cookie_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
        except Exception:
            pass

        host = wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#gallery-leaflet"))
        )

        shadow_root = wait.until(
            lambda d: d.execute_script("return arguments[0].shadowRoot", host)
        )

        slides_count = driver.execute_script(
            "return arguments[0].querySelectorAll('div.embla__slide').length;",
            shadow_root
        )

        next_btn = driver.execute_script(
            """
            const buttons = arguments[0].querySelectorAll(
              'button.inline-flex.items-center.justify-center.gap-2.whitespace-nowrap.rounded-md.text-sm.font-medium.transition-colors'
            );
            return buttons[1] || buttons[buttons.length - 1] || null;
            """,
            shadow_root
        )

        pics = []

        for i in range(slides_count):
            imgs = driver.execute_script(
                """
                const root = arguments[0];
                const idx = arguments[1];
                const slides = root.querySelectorAll('div.embla__slide');
                const slide = slides[idx];
                if (!slide) return [];
                // на одном слайде может быть 2 img (разворот)
                return Array.from(slide.querySelectorAll('img')).map(img => ({
                    src: img.getAttribute('src'),
                    dataSrc: img.getAttribute('data-src'),
                    srcset: img.getAttribute('srcset'),
                }));
                """,
                shadow_root,
                i
            )

            need_retry = (not imgs) or all(
                im["src"] and im["src"].startswith("data:image") for im in imgs
            )
            if need_retry:
                driver.execute_script(
                    "arguments[0].querySelectorAll('div.embla__slide')[arguments[1]].scrollIntoView({block: 'center'});",
                    shadow_root,
                    i
                )
                time.sleep(0.5)
                imgs = driver.execute_script(
                    """
                    const root = arguments[0];
                    const idx = arguments[1];
                    const slides = root.querySelectorAll('div.embla__slide');
                    const slide = slides[idx];
                    if (!slide) return [];
                    return Array.from(slide.querySelectorAll('img')).map(img => ({
                        src: img.getAttribute('src'),
                        dataSrc: img.getAttribute('data-src'),
                        srcset: img.getAttribute('srcset'),
                    }));
                    """,
                    shadow_root,
                    i
                )

            for im in imgs:
                real_url = im["src"]
                if real_url and not real_url.startswith("data:image"):
                    pics.append(real_url)

            if i < slides_count - 1 and next_btn:
                driver.execute_script("arguments[0].click();", next_btn)
                time.sleep(0.4)

        driver.quit()
        return pics