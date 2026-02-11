from abc import ABC, abstractmethod
import requests

class BaseParser(ABC):
    @abstractmethod
    def get_all_flyers(self) -> list:
        pass

    @abstractmethod
    def get_pictures(self, url: str) -> list:
        pass

    def save_image(self, url: str, path: str) -> None:
        resp = requests.get(url)
        resp.raise_for_status()
        with open(f"{path}_1.png", "wb") as f:
            f.write(resp.content)

    def save_images_interface(self, link: str, path: str) -> None:
        list_of_pictures = self.get_pictures(link)
        for i in range(len(list_of_pictures)):
            self.save_image(list_of_pictures[i], path)