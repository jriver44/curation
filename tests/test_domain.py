# tests/test_domain.py

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from services import CollectionService
from domain import Collection

def make_service() -> CollectionService:
    return CollectionService()

def get_item_by_name(collection: Collection, name: str):
    return next(i for i in collection.items if i.name == name)

def test_add_single_item_creates_new_entry():
    collection = Collection(name="test")
    
    services = make_service()
    
    collection = services.add_item(
        collection,
        name="Padron x000",
        category="cigar",
        quantity=2,
    )
    
    item = get_item_by_name(collection, "Padron x000")
    
    assert item.name == "Padron x000"
    assert item.category == "cigar"
    assert item.quantity == 2
    
def test_add_same_item_increments_quantity():
    collection = Collection(name="test")
    
    services = make_service()
    
    
    
    collection = services.add_item(
        collection, 
        name="Arturo Fuente", 
        category="cigar", 
        quantity=1,
    )
    collection = services.add_item(
        collection, 
        name="Arturo Fuente", 
        category="cigar", 
        quantity=3,
    )
    
    item = get_item_by_name(collection, "Arturo Fuente")
    
    assert item.quantity == 4