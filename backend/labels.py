from dotenv import load_dotenv
load_dotenv()

from utils.json_parse import get_city_data, save_city_labels
from pathlib import Path
from geolocation_summarizer.hierarchical_summarizer import summarize_data
import asyncio
from utils.args import Args
import os


def generate_city_labels(city, level):
    city_data = get_city_data(city)
    args = Args(
        api_key=os.getenv("GEMINI_API_KEY"),
        grid_delta=0.01,
        provider="gemini",
        batch_size=30,
        tags_data=city_data.tags,
        lat=None,
        lon=None,
        tag=None,
        existing_results=None,
    )
    results = asyncio.run(summarize_data(args))
    save_city_labels(city, results)
    return results


def get_city_labels(city, level):
    level = int(level)
    city_data = get_city_data(city, levels=True)
    return city_data.levels.get(level, [])


def add_label(city, data):
    label = None
    pass

if __name__ == "__main__":
    city = "delhi"
    level = "2"
    labels = get_city_labels(city, level)
    print(len(labels))
    print(labels[:3])