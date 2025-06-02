from main.importers.base import BaseImporter
from main.importers.apple.parser import parse_apple_export

class AppleImporter(BaseImporter):
    def parse(self) -> dict:
        return parse_apple_export(self.file)
