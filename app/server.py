from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Database

from app.services.utils import clean_path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/promotions")
def get_promotions(category: str | None = None, store: str | None = None, promotion: str | None = None):
    db = Database()
    try:
        promotions = db.get_promotions_filtered(category=category, store=store, promotion=promotion)
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


@app.get("/api/stores")
def get_active_chains():
    db = Database()
    try:
        active_chains = db.get_unique_active_chains()
        return {"stores": active_chains}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()


@app.get("/api/promotions-types")
def get_promotion_names():
    db = Database()
    try:
        promotions_names = db.get_unique_active_promotions_names()
        return {"promotion_types": promotions_names}
    except Exception as e:
        return {"error": str(e)}
    finally:
        db.close()
