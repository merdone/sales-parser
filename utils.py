import os
import base64
import json
import re
from dotenv import load_dotenv

OCR_PROMPT_PATH = "prompts/ocr_system_prompt.txt"
IMAGE_PROMPT_PATH = "prompts/image_system_prompt.txt"

path_dict = {"ocr": OCR_PROMPT_PATH,
             "image": IMAGE_PROMPT_PATH}


def convert_from_text_to_grams(weight_text: str) -> int | None:
    if not weight_text:
        return None

    text = weight_text.lower().replace(',', '.').strip()

    is_correct = re.match(r"(\d+(\.\d+)?)\s*g", text)
    if is_correct:
        return int(float(is_correct.group(1)))

    is_correct = re.match(r"(\d+)\s*[x×]\s*(\d+(\.\d+)?)\s*g", text)
    if is_correct:
        count = int(is_correct.group(1))
        unit = float(is_correct.group(2))
        return int(count * unit)

    return None


def load_prompt(type_of_prompt: str) -> str:
    if type_of_prompt in ["ocr", "image"]:
        with open(path_dict[type_of_prompt], "r", encoding="utf-8") as file:
            return file.read()
    else:
        return None


def load_database():
    load_dotenv()
    return {
        "host": os.getenv("host"),
        "dbname": os.getenv("dbname"),
        "user": os.getenv("user"),
        "password": os.getenv("password"),
        "port": os.getenv("port"),
    }


def load_api_key(type_of_key: str) -> str:
    load_dotenv()
    if type_of_key == "google":
        key_json = os.getenv("GOOGLE_CLOUD_KEY")
        return json.loads(key_json)
    elif type_of_key == "open_ai":
        return os.getenv("OPENAI_KEY")
    else:
        return None


def encode_image_to_base64(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No image on path: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        raise IOError(f"Mistake while reading image {image_path}: {e}")


def write_to_file(content, name):
    with open(f"{name}.json", "w", encoding="utf-8") as file:
        json.dump(
            content,
            file,
            ensure_ascii=False,
            indent=2
        )
