from walrusdb.walrus_dbo import DBO
from walrusdb.types import DatabaseDefinition, CollectionDefinition, IndexDefinition
from walrusdb.collection import Collection
from walrusdb.index import Index


class Database:
    def __init__(self):
        self.dbo = DBO()
        self.blob_id = None

    def load_database(self, blob_id):
        self.blob_id = blob_id
        data = self.dbo.get_blob_data(blob_id)
        self.database = DatabaseDefinition(**data)

    def update_database_blob(self):
        self.blob_id = self.dbo.update_blob(
            blob_id=self.database.blob_id,
            updates=self.database.model_dump(),
        )
        return self.blob_id

    def create_database(self, name, collections={}, indexes={}):
        self.database = DatabaseDefinition(
            name=name,
            collections=collections,
            indexes=indexes,
        )
        self.blob_id = self.dbo.create_blob_from_data(self.database.model_dump_json())
        return self.blob_id
    
    def get_database_name(self):
        return self.database.name

    def get_collections(self):
        return self.database.collections

    def get_indexes(self):
        return self.database.indexes

    def add_collection(self, name, fields, data):
        data = data or []
        collection_id = Collection().create_collection(fields, data)
        self.database.collections[name] = CollectionDefinition(name, fields, collection_id)
        return self.update_database_blob()
    
    def delete_collection(self, name):
        if name not in self.database.collections:
            raise ValueError(f"Collection {name} does not exist")
        del self.database.collections[name]
        return self.update_database_blob()