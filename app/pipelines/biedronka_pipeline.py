from app.parsers.base_parser import BaseParser
from app.parsers.biedronka_parser import BiedronkaParser
from app.pipelines.base_pipeline import BasePipeline


class BiedronkaPipeLine(BasePipeline):
    def get_store_name(self) -> str:
        return "biedronka"

    def get_parser(self) -> BaseParser:
        return BiedronkaParser()
