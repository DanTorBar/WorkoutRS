from main.importers.base import BaseImporter
from main.importers.fitbit.parser import parse_fitbit_export

class FitbitImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_fitbit_export(self.file)
