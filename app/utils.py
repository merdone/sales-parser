from pathlib import Path
import hashlib
import os
import base64
import json
import re
import time
from unidecode import unidecode

from functools import wraps


def timer(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        t1 = time.perf_counter()
        result = func(*args, **kwargs)
        t2 = time.perf_counter()
        elapsed = t2 - t1
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result

    return wrapper


def async_timer(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        t1 = time.perf_counter()
        result = await func(*args, **kwargs)
        t2 = time.perf_counter()
        elapsed = t2 - t1
        print(f"{func.__name__} took {elapsed:.2f} seconds")
        return result

    return wrapper


def get_flyer_id(url: str) -> str:
    hash_object = hashlib.md5(url.encode())
    return hash_object.hexdigest()[:10]


def setup_flyer_dirs(store_name: str, flyer_url: str) -> dict:
    flyer_id = get_flyer_id(flyer_url)
    base_dir = Path("data") / store_name / flyer_id

    dirs = {
        "root": base_dir,
        "raw": base_dir / "raw",
        "crops": base_dir / "crops",
        "json": base_dir / "json"
    }

    dirs["raw"].mkdir(parents=True, exist_ok=True)
    dirs["crops"].mkdir(parents=True, exist_ok=True)
    dirs["json"].mkdir(parents=True, exist_ok=True)

    return dirs


def get_safe_filename(text: str, max_len: int = 50) -> str:
    if not text:
        return "product"

    text = unidecode(text)
    text = text.lower()

    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w\-]", "_", text)
    text = re.sub(r"_+", "_", text)

    if len(text) > max_len:
        text = text[:max_len]
    return text.strip("_") or "product"


def load_json(path, default=None):
    path = Path(path)
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {path}: {e}") from e


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


def encode_image_to_base64(image_path: Path) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No image on path: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        raise IOError(f"Mistake while reading image {image_path}: {e}")


def save_to_json(promotions, output_dir):
    saved_files = []
    for idx, promotion in enumerate(promotions):
        filename = f"{idx:03d}.json"
        full_path = output_dir / filename
        with open(full_path, "w", encoding="utf-8") as file:
            json.dump(
                promotion,
                file,
                ensure_ascii=False,
                indent=2
            )
        saved_files.append(full_path)
    return saved_files