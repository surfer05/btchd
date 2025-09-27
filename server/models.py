from walrusdb.database import Database
import os

database_id = os.environ.get("WALRUS_DB_ID", None)
if database_id is None:
    raise ValueError("WALRUS_DB_ID environment variable not set")

db = Database()
db.load_database(database_id)


def get_label_collection():
    collections = db.get_collections()
    if "labels" not in collections:
        raise ValueError("Labels collection not found in database")
    label_collection_id = collections["labels"].collection_id
    label_collection = db.dbo.get_blob_data(label_collection_id)
    return label_collection