import asyncio

from app.gpt import Extractor
from app.pipelines.biedronka_pipeline import BiedronkaPipeLine

from app.database import Database

async def main():
    db = Database()
    gpt = Extractor()
    try:
        biedronka = BiedronkaPipeLine(gpt, db)
        await biedronka.run()
    finally:
        await gpt.close()
        db.close()

if __name__ == '__main__':
    asyncio.run(main())
