from importers.base import BaseImporter
from .parser import parse_fitbit_export

class FitbitImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_fitbit_export(self.file)
