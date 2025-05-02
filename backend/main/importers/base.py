from abc import ABC, abstractmethod

class BaseImporter(ABC):
    def __init__(self, upload_file):
        """Recibe un File object de Django"""
        self.file = upload_file

    @abstractmethod
    def parse(self) -> dict:
        """Devuelve un dict con las claves del modelo HealthProfile"""
        pass