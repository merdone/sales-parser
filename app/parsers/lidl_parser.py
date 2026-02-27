import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from app.parsers.base_parser import BaseParser
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class LidlParser(BaseParser):
    def get_basic_url(self) -> str:
        return "https://www.lidl.pl/c/nasze-gazetki/s10008614"

    def get_all_flyers(self) -> list:
        links = []
        r = requests.get(self.get_basic_url(), headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        section = soup.find("div", {"class": "leaflets-overview__content"}).find("div", {"class": "subcategory"})
        elements = section.find_all("a", {"class": "flyer"})
        for element in elements:
            links.append(element.get("href"))
        return links

    def get_pictures(self, url: str) -> list:
        driver = webdriver.Firefox()
        driver.get(url)
        wait = WebDriverWait(driver, 20)

        try:
            cookie_btn = wait.until(
                EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler"))
            )
            cookie_btn.click()
            time.sleep(1)
        except Exception:
            pass

        time.sleep(3)

        pics = []
        max_pages = 100
        empty_retries = 0
        for _ in range(max_pages):
            imgs = driver.find_elements(By.TAG_NAME, "img")
            new_pics_found = False

            for img in imgs:
                src = img.get_attribute("src")
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

            ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()

            time.sleep(1.5)
        driver.quit()
        return pics[1:]