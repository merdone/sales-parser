from abc import ABC, abstractmethod
from pathlib import Path
import requests

class BaseParser(ABC):
    @abstractmethod
    def get_all_flyers(self) -> list:
        pass

    @abstractmethod
    def get_pictures(self, url: str) -> list:
        pass

    @abstractmethod
    def get_basic_url(self) -> str:
        pass

    @classmethod
    def save_image(cls, url: str, save_path: Path) -> None:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)

    def download_flyer(self, flyer_link: str, output_dir: Path) -> list[Path]:
        list_of_pictures = self.get_pictures(flyer_link)
        saved_files = []
        for idx, img_url in enumerate(list_of_pictures):
            filename = f"{idx:03d}.png"
            full_path = output_dir / filename
            self.save_image(img_url, full_path)
            saved_files.append(full_path)
        return saved_files