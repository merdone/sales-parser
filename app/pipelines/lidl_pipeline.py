from app.parsers.base_parser import BaseParser
from app.parsers.lidl_parser import LidlParser
from app.pipelines.base_pipeline import BasePipeline


class LidlPipeLine(BasePipeline):
    def _get_store_name(self) -> str:
        return "lidl"

    def _get_parser(self) -> BaseParser:
        return LidlParser()
