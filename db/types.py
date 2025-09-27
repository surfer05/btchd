from typing import Dict, List, Optional, Union, Type
from pydantic import BaseModel


# Database
# ------------------------

class IndexDefinition(BaseModel):
    name: str
    field: str
    type: str  # "string" | "number"
    index_file: str


class CollectionDefinition(BaseModel):
    name: str
    fields: Dict[str]
    indexes: List[str] 
    collection_file: str


class DatabaseDefinition(BaseModel):
    name: str
    collections: Dict[str, CollectionDefinition]
    indexes: Dict[str, IndexDefinition]


# Collections
# ------------------------

class CollectionDocument(BaseModel):
    documents: List[str]  # blob_ids


# Index Files
# ------------------------

class StringIndex(BaseModel):
    mapping: Dict[str, List[str]]  # value -> list of blob_ids


class BTreeNode(BaseModel):
    key: int
    doc_ids: Optional[List[str]] = None
    left: Optional["BTreeNode"] = None
    right: Optional["BTreeNode"] = None


class NumericIndex(BaseModel):
    root: BTreeNode


BTreeNode.model_rebuild()


# Nodes
# ------------------------

STRING_TO_FIELD = {
    'str'   : str,
    'int'   : int,
    'float' : float,
}