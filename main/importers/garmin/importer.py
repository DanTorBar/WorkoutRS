from importers.base import BaseImporter
from .parser import parse_garmin_export

class GarminImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_garmin_export(self.file)
