import sys
# sys.path.insert(0, "")
print(sys.path)

from walrusdb.database import Database
from utils.json_parse import get_city_data


def setup_database():
    # db = Database()
    # database_id = db.create_database(name="btchd")
    # print(f"Created database with ID: {database_id}")

    city = "delhi"
    city_data = get_city_data(city=city)

    tag_keys = {
        "label": "tag",
        "latitude": "latitude",
        "longitude": "longitude",
        "uid": "uid",
    }
    tag_data = [
        {key: tag[val] for key, val in tag_keys} | {"city": city}
        for tag in city_data.tags
    ]
    print(tag_data[0])
    # tag_data = [tag | {"city": city} for tag in tag_data]
    # db.add_collection(
    #     name="labels",
    #     fields=["label", "latitude", "longitude", "uid"],
    #     data=tag_data,
    # )

    cat_keys = {
        "category": "category",
        "latitude": "latitude",
        "longitude": "longitude",
        "count": "count",
    }
    cat_data = [
        {key: cat[val] for key, val in cat_keys} | {"city": city}
        for cat in city_data.oneDecimalLessAllUsersPaths
    ]

    # db.add_collection(
    #     name="categories",
    #     fields=["category", "latitude", "longitude", "count"],
    #     data=cat_data,
    # )
