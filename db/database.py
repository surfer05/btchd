from db.walrus_dbo import DBO
from db.types import DatabaseDefinition


class Database:
    def __init__(self):
        self.dbo = DBO()

    def load_database(self, blob_id):
        data = self.dbo.get_blob_data(blob_id)
        self.database = DatabaseDefinition(**data)

    def create_database(self, name, collections={}, indexes={}):
        self.database = DatabaseDefinition(
            name=name,
            collections=collections,
            indexes=indexes,
        )
        return self.dbo.create_blob_from_data(self.database.model_dump_json())

    def get_database_name(self):
        return self.database.name

    def get_collection(self):
        return self.database.collections

    def get_indexes(self):
        return self.database.indexes

    def add_collection(self, name, fields, indexed_fields):
        pass
