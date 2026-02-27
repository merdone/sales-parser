import asyncio

from app.gpt import Extractor
from app.pipelines.biedronka_pipeline import BiedronkaPipeLine

from app.database import Database

#TODO 1) loging 3) Scheduler 4) FrontEnd -> React 5) docker 7) server

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
