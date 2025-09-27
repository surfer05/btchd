from typing import Dict, List, Optional, Union
from pydantic import BaseModel


# Top level structure
# ------------------------

class IndexDefinition(BaseModel):
    id: str
    name: str
    field: str
    type: str  # "string" | "number"
    index_file: str


class CollectionDefinition(BaseModel):
    id: str
    name: str
    fields: List[str]
    indexes: List[str] 
    collection_file: str


class DatabaseDefinition(BaseModel):
    collections: Dict[str, CollectionDefinition]
    indexes: Dict[str, IndexDefinition]


# Collections
# ------------------------

class CollectionDocuments(BaseModel):
    collection_id: str
    documents: List[str]  # blob_ids


# Index Files
# ------------------------

class StringIndex(BaseModel):
    mapping: Dict[str, List[str]]  # value -> list of blob_ids


class BTreeNode(BaseModel):
    keys: List[int]
    doc_ids: Optional[List[str]] = None
    children: Optional[List["BTreeNode"]] = None


class NumericIndex(BaseModel):
    root: BTreeNode


BTreeNode.model_rebuild()
