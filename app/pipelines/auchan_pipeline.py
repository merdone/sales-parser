from app.parsers.auchan_parser import AuchanParser
from app.pipelines.base_pipeline import BasePipeline

from app.parsers.base_parser import BaseParser

class AuchanPipeLine(BasePipeline):
    def _get_store_name(self) -> str:
        return "auchan"

    def _get_parser(self) -> BaseParser:
        return AuchanParser()