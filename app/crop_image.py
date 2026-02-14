from pathlib import Path

from PIL import Image

def mask_to_position_bbox(mask):
    if not mask:
        return None

    xs = [float(p.get("x", 0)) for p in mask]
    ys = [float(p.get("y", 0)) for p in mask]

    left = max(0.0, min(xs))
    right = min(100.0, max(xs))
    top = max(0.0, min(ys))
    bottom = min(100.0, max(ys))

    width = max(0.0, right - left)
    height = max(0.0, bottom - top)

    if width <= 0 or height <= 0:
        return None

    return {"left": left, "top": top, "width": width, "height": height}

def crop_products(img_path: Path, promotions: list[dict]) -> None:
    if not img_path.exists():
        print(f"[ERROR] Image not found: {img_path}")
        return

    with Image.open(img_path) as img:
        width, height = img.size
        for promotion in promotions:
            mask = promotion.get("mask")
            pos = mask_to_position_bbox(mask)
            save_path = Path(promotion.get("crop_path"))
            if not mask or not save_path:
                return

            if not pos:
                return

            left_p = float(pos.get("left", 0))
            top_p = float(pos.get("top", 0))
            width_p = float(pos.get("width", 0))
            height_p = float(pos.get("height", 0))

            x1 = int(width * left_p / 100.0)
            y1 = int(height * top_p / 100.0)
            x2 = int(width * (left_p + width_p) / 100.0)
            y2 = int(height * (top_p + height_p) / 100.0)

            x1 = max(0, min(width, x1))
            x2 = max(0, min(width, x2))
            y1 = max(0, min(height, y1))
            y2 = max(0, min(height, y2))

            if x2 <= x1 or y2 <= y1:
                return

            save_path.parent.mkdir(parents=True, exist_ok=True)
            crop = img.crop((x1, y1, x2, y2))
            crop.save(save_path)