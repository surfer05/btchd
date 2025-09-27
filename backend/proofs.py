from utils.json_parse import read_json_file
from pathlib import Path
import json


def get_proofs_data():
    file_path = Path(__file__).parent.parent / "data" / "proofs.json"
    data = read_json_file(file_path)
    return data


def add_proof(proof):
    data = get_proofs_data()
    if data is None:
        data = []
    data.append(proof)
    file_path = Path(__file__).parent.parent / "data" / "proofs.json"
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving proof: {e}")