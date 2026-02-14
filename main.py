import asyncio

from app.gpt import Extractor
from app.pipelines.biedronka_pipeline import BiedronkaPipeLine

from app.database import Database

async def main():
    gpt = Extractor()
    try:
        biedronka = BiedronkaPipeLine(gpt)
        await biedronka.run()
    finally:
        await gpt.close()
    # db = Database()


if __name__ == '__main__':
    asyncio.run(main())
