from db.walrus_dbo import DBO
from db.types import StringIndex, NumericIndex
from db.utils import validate_objects
from collections import defaultdict

class Index:
    def __init__(self):
        self.dbo = DBO()

    def load_index(self, blob_id):
        data = self.dbo.get_blob_data(blob_id)
        self.index = Index(**data)

    def create_index(self, field, type, objects, ids):
        data = self._create_id_to_object_mapping(objects, ids)
        if type == "str":
            index = self._create_string_index(field, data)
        else:
            index = self._create_number_index(field, data)

    def _create_id_to_object_mapping(self, objects, ids):
        if len(ids) != len(objects):
            raise ValueError("Cannot make ID, object mapping")
        return {ids[i]: objects[i] for i in range(len(ids))}
    
    def _create_string_index(self, objects):
        mapping = defaultdict([])
        for id, obj in objects.items():
            mapping[obj].append(id)
        return mapping
    
    def _create_number_index(self, objects):
        pass
    