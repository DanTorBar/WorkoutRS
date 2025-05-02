from importers.base import BaseImporter
from .parser import parse_googlefit_export

class GoogleFitImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_googlefit_export(self.file)
