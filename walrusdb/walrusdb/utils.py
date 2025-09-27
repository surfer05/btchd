from walrusdb.types import STRING_TO_FIELD
from typing import List, Dict, Any


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def validate_objects(
    schema: Dict[str, str], objects: List[Dict[str, Any]]
) -> List[bool]:
    """
    Validate a list of objects against a schema.

    :param schema: Dict with field_name -> expected_type (str, int, float).
    :param objects: List of objects (dicts) to validate.
    :return: List of booleans, one per object (True if valid, False otherwise).
    """
    for obj in objects:
        for field, expected_type_str in schema.items():
            expected_type = STRING_TO_FIELD[expected_type_str]
            if field not in obj:
                return False
            value = obj[field]
            if not isinstance(value, expected_type):
                # Allow int where float is expected
                if expected_type is float and isinstance(value, int):
                    continue
                return False
    return True
