import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import Database

from app.services.utils import clean_path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
static_dir = os.path.join(root_dir, "static")
data_dir = os.path.join(root_dir, "data")


@app.get("/")
async def serve_root():
    return FileResponse(os.path.join(static_dir, "index.html"))


@app.get("/static/index.html")
async def serve_index_explicit():
    return FileResponse(os.path.join(static_dir, "index.html"))


app.mount("/static", StaticFiles(directory=static_dir), name="static")

if os.path.exists(data_dir):
    app.mount("/images", StaticFiles(directory=data_dir), name="images")


@app.get("/api/promotions")
def get_promotions(category: str | None = None):
    db = Database()
    try:
        if category and category != "Wszystko":
            promotions = db.get_all_promotions_by_category(category)
        else:
            promotions = db.get_all_promotions()

        for promotion in promotions:
            raw_path = promotion.get("image_path")
            if raw_path:
                promotion["image_url"] = f"/images/{clean_path(raw_path)}"

            raw_source = promotion.get("source_image_path")
            if raw_source:
                promotion["source_image_url"] = f"/images/{clean_path(raw_source)}"

        return promotions
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()