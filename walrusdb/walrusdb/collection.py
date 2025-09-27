from walrusdb.walrus_dbo import DBO
from walrusdb.types import CollectionDocument, Object
from walrusdb.utils import validate_objects
from collections import defaultdict


class Collection:
    def __init__(self):
        self.blob_id = None
        self.dbo = DBO()

    def load_collection(self, blob_id):
        self.blob_id = blob_id
        data = self.dbo.get_blob_data(blob_id)
        self.collection = CollectionDocument(**data)

    def update_collection_blob(self):
        self.blob_id = self.dbo.update_blob(
            blob_id=self.collection.blob_id,
            updates=self.collection.model_dump(),
        )
        return self.blob_id

    def create_collection(self, fields, data):
        if not validate_objects(fields):
            raise ValueError("Data validation failed")
        documents = self.create_objects(data)
        self.collection = CollectionDocument(documents=documents)
        self.blob_id = self.dbo.create_blob_from_data(self.collection.model_dump_json())
        return self.blob_id

    def create_documents(self, objects):
        return [self.dbo.create_blob_from_data(obj) for obj in objects]

    def get_documents(self):
        return self.collection.documents

    def add_documents(self, objects):
        new_docs = self.create_documents(objects)
        self.collection.documents.extend(new_docs)
        return self.update_collection_blob()

    def delete_documents(self, blob_ids):
        self.collection.documents = [
            doc for doc in self.collection.documents if doc not in blob_ids
        ]
        return self.update_collection_blob() 

    def update_documents(self, updates: dict):
        docs = defaultdict(str)
        blob_ids = updates.keys()
        for blob_id in blob_ids:
            if blob_id not in self.collection.documents:
                raise ValueError(f"Document with blob_id {blob_id} not found in collection")
        for blob_id, update in updates.items():
            new_blob_id = self.dbo.update_blob(blob_id, update, partial=True)
            docs[blob_id] = new_blob_id
        for blob_id, new_blob_id in docs.items():
            self.collection.documents.remove(blob_id)
            self.collection.documents.append(new_blob_id)
        return self.update_collection_blob()
