from walrusdb.walrus_dbo import DBO
from walrusdb.types import StringIndex, NumericIndex
from walrusdb.utils import validate_objects
from collections import defaultdict


class Index:
    def __init__(self):
        self.dbo = DBO()
        self.blob_id = None
        self.index = None

    def load_index(self, blob_id, type):
        data = self.dbo.get_blob_data(blob_id)
        if type == "str":
            self.index = StringIndex(**data)
        else:
            self.index = NumericIndex(**data)

    def upadate_index_blob(self):
        self.blob_id = self.dbo.update_blob(
            blob_id=self.index.blob_id,
            updates=self.index.model_dump(),
        )

    def create_index(self, field, type, objects, ids):
        data = self._create_id_to_object_mapping(objects, ids)
        if type == "str":
            self.index = self._create_string_index(field, data)
        else:
            self.index = self._create_number_index(field, data)
        self.blob_id = self.dbo.create_blob_from_data(self.index.model_dump_json())
        return self.blob_id

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

    # TODO: search and filter methods
    def search(self, value):
        if isinstance(self.index, StringIndex):
            return self.index.mapping.get(value, [])
        else:
            raise NotImplementedError("Numeric index search not implemented yet")
        
