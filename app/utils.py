from pathlib import Path
import os
import base64
import json
import re
import time

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


def get_safe_filename(text: str, max_len: int = 50) -> str:
    if not text:
        return "product"
    text = text.strip()
    text = re.sub(r"\s+", "_", text)
    text = re.sub(r"[^\w\-]", "_", text)
    if len(text) > max_len:
        text = text[:max_len]
    return text or "product"


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


def encode_image_to_base64(image_path: str) -> str:
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"No image on path: {image_path}")

    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except IOError as e:
        raise IOError(f"Mistake while reading image {image_path}: {e}")


def save_to_json(content, name):
    with open(f"{name}.json", "w", encoding="utf-8") as file:
        json.dump(
            content,
            file,
            ensure_ascii=False,
            indent=2
        )
