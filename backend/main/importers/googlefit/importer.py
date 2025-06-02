from main.importers.base import BaseImporter
from main.importers.googlefit.parser import parse_googlefit_export

class GoogleFitImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_googlefit_export(self.file)
