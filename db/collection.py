from db.walrus_dbo import DBO
from db.types import CollectionDocument
from db.utils import validate_objects

class Collection:
    def __init__(self):
        self.dbo = DBO()

    def load_collection(self, blob_id):
        data = self.dbo.get_blob_data(blob_id)
        self.collection = CollectionDocument(**data)

    def create_collection(self, fields, data):
        if not validate_objects(fields):
            raise ValueError("Data validation failed")
        documents = self.create_objects(data)
        self.collection = CollectionDocument(documents=documents)
        return self.dbo.create_blob_from_data(self.collection.model_dump_json())
    
    def create_objects(self, objects):
        return [self.dbo.create_blob_from_data(obj) for obj in objects]
    
    def get_documents(self):
        return self.collection.documents
        