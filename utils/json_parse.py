from datetime import datetime
import json
from pathlib import Path


class CityData:
    def __init__(self, file_path: str, labels_file_path: str = None):
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

        if labels_file_path is not None:
            self.levels = get_labels_data(labels_file_path)

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


def get_labels_data(file_path):
    data = read_json_file(file_path)
    levels = {}
    for level, point in data.get("levels").items():
        labels = []
        for _, label_data in point.items():
            bounds = label_data.get("kernel_boundaries")
            lat = (bounds["max_lat"] + bounds["min_lat"]) / 2
            lon = (bounds["max_lon"] + bounds["min_lon"]) / 2
            tag = label_data.get("combined_tag").get("summary")
            confidence = label_data.get("combined_tag").get("confidence")
            labels.append({
                "level": level,
                "lat": lat,
                "lon": lon,
                "tag": tag,
                "confidence": confidence,
            })
        levels[int(level)] = labels
    return levels


def get_city_data(city, levels=False):
    city = city.lower()
    file_path = Path(__file__).parent.parent / "data" / f"{city}.json"
    if levels:
        labels_file_path = Path(__file__).parent.parent / "data" / f"{city}_labels.json"
        city_data = CityData(file_path, labels_file_path)
    else:
        city_data = CityData(file_path)
    return city_data


def save_city_labels(city, labels_data):
    city = city.lower()
    file_path = Path(__file__).parent.parent / "data" / f"{city}_labels.json"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(labels_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving labels: {e}")


if __name__ == "__main__":
    file_path = Path(__file__).parent.parent / "data" / "delhi.json"
    json_data = read_json_file(file_path)
