from utils.json_parse import CityData
from pathlib import Path
from geolocation_summarizer.hierarchical_summarizer import summarize_data
import asyncio
from utils.args import Args
from dotenv import load_dotenv
load_dotenv()
import os

def get_city_data(city):
    file_path = Path(__file__).parent.parent / "data" / f"{city}.json"
    city_data = CityData(file_path)
    return city_data

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
    coords_data = results["levels"][f"{level}"]
    output = []
    for key, coord in coords_data.items():
        bounds = coord["kernel_boundaries"]
        mean_lat = (bounds["min_lat"] + bounds["max_lat"])/2
        mean_lon = (bounds["min_lon"] + bounds["max_lon"])/2
        label = coord["combined_tag"]
        output.append({
            "label": label,
            "lat": mean_lat,
            "lon": mean_lon,
            "strength": 1,
        })
    return output
        

def add_city_labes(city, lat, lon, tag):
    city_data = get_city_data(city)
    args = Args(
        api_key="abc123",
        grid_delta=0.01,
        provider="gemini",
        batch_size=30,
        tags_data=city_data.tags,
        lat=None,
        lon=None,
        tag=None,
        existing_results=None,
    )