from pathlib import Path

from PIL import Image

from utils import get_safe_filename, load_json


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


def crop_products(image_path: str, json_path: str, out_dir: str) -> None:
    img_path = Path(image_path)
    js_path = Path(json_path)
    out_path = Path(out_dir)

    out_path.mkdir(parents=True, exist_ok=True)

    if not img_path.exists():
        print(f"[ERROR] Image not found: {img_path}")
        return
    if not js_path.exists():
        print(f"[ERROR] JSON not found: {js_path}")
        return

    img = Image.open(img_path)
    W, H = img.size

    data = load_json(js_path)

    products = data["promotions"]

    for idx, item in enumerate(products):
        mask = item.get("mask")
        pos = mask_to_position_bbox(mask)
        raw_name = item.get("product_name")

        if not pos:
            print(f"[WARN] No valid position/mask for item {idx}: {raw_name!r}")
            continue

        left_p = float(pos.get("left", 0))
        top_p = float(pos.get("top", 0))
        width_p = float(pos.get("width", 0))
        height_p = float(pos.get("height", 0))

        x1 = int(W * left_p / 100.0)
        y1 = int(H * top_p / 100.0)
        x2 = int(W * (left_p + width_p) / 100.0)
        y2 = int(H * (top_p + height_p) / 100.0)

        x1 = max(0, min(W, x1))
        x2 = max(0, min(W, x2))
        y1 = max(0, min(H, y1))
        y2 = max(0, min(H, y2))

        if x2 <= x1 or y2 <= y1:
            print(f"[WARN] Bad box for item {idx}: {raw_name!r}")
            continue

        crop = img.crop((x1, y1, x2, y2))

        base = get_safe_filename(raw_name)
        filename = f"{idx:02d}_{base}.png"
        crop_path = out_path / filename
        crop.save(crop_path)