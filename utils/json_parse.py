from datetime import datetime
import json
from pathlib import Path


class CityData:
    def __init__(self, file_path: str):
        data = read_json_file(file_path)
        if not data.get('success'):
            raise ValueError("Invalid Json Data")
        self.epoch_generated = data.get('epoch_generated')
        self.slug = data.get('slug')
        self.cityName = data.get('cityName')
        self.latitude = data.get('latitude')
        self.longitude = data.get('longitude')
        self.tags = data.get('tags')
        self.noDecimalLessAllUsersPaths = data.get('noDecimalLessAllUsersPaths')
        self.oneDecimalLessAllUsersPaths = data.get('oneDecimalLessAllUsersPaths')
        self.highZoomUsersPaths = data.get('highZoomUsersPaths')
        self.homePrices = data.get('homePrices')
        self.rentPrices = data.get('rentPrices')
        self.cafes = data.get('cafes')
        self.coworkings = data.get('coworkings')
        self.colors = data.get('colors')
        self.hipsterCenter = data.get('hipsterCenter')
        self.preHipsterCenter = data.get('preHipsterCenter')
        self.neighborhoodsGeoJSONAvailable = data.get('neighborhoodsGeoJSONAvailable')
        self.neighborhoodsGeoJSONURL = data.get('neighborhoodsGeoJSONURL')

    @property
    def date_generated(self):
        return datetime.fromtimestamp(self.epoch_generated).strftime('%Y-%m-%d')


def read_json_file(file_path: str):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: File not found → {file_path}")
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON format → {e}")
    return None


def get_city_data(city):
    city = city.lower()
    file_path = Path(__file__).parent.parent / "data" / f"{city}.json"
    city_data = CityData(file_path)
    return city_data


if __name__ == "__main__":
    file_path = Path(__file__).parent.parent / "data" / "delhi.json"
    json_data = read_json_file(file_path)
