import os
from walrusdb.database import Database
from utils.json_parse import get_city_data


def setup_database():
    db = Database()
    database_id = os.environ.get("WALRUS_DB_ID", None)
    if database_id is None:
        database_id = db.create_database(name="btchd")
        print(f"Created database with ID: {database_id}")
    else:
        db.load_database(database_id)

    city = "delhi"
    city_data = get_city_data(city=city)

    tag_keys = {
        "label": "tag",
        "latitude": "latitude",
        "longitude": "longitude",
        "uid": "uid",
    }
    tag_data = [
        {key: tag[val] for key, val in tag_keys.items()} | {"city": city}
        for tag in city_data.tags
    ]
    tag_fields = {
        "label": "str",
        "latitude": "float",
        "longitude": "float",
        "uid": "str",
    }
    tag_data = tag_data[:15]
    db.add_collection(
        name="labels",
        fields=tag_fields,
        data=tag_data,
    )

    cat_keys = {
        "category": "category",
        "latitude": "latitude",
        "longitude": "longitude",
        "count": "samples",
    }
    cat_data = [
        {key: cat[val] for key, val in cat_keys.items()} | {"city": city}
        for cat in city_data.oneDecimalLessAllUsersPaths
    ]
    cat_fields = {
        "label": "str",
        "latitude": "float",
        "longitude": "float",
        "count": "int",
    }
    cat_data = cat_data[:15]
    db.add_collection(
        name="categories",
        fields=cat_fields,
        data=cat_data,
    )
    print(db.blob_id)


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    setup_database()
