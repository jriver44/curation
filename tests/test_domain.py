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
    target = _norm(name)
    return next((i for i in collection.items if _norm(i.name) == target), None)

def _norm(s: str) -> str:
    return s.strip().casefold()

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
    
def test_remove_item():
    collection = Collection(name="test")
    
    services = make_service()
    
    collection = services.add_item(
        collection,
        name="Padron x000",
        category="cigar",
        quantity=2,
    )
    
    services.remove_item(collection, "Padron x000", "cigar", 1)
    
    item = get_item_by_name(collection, "Padron x000")
    
    assert item.quantity == 1
    
def test_remove_item_removes_entry_when_exact():
    collection = Collection(name="test")
    
    service = make_service()
    
    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        2,
    )
    
    service.remove_item(collection, "Padron x000", "cigar", 2)
    
    item = get_item_by_name(collection, "Padron x000")
    
    assert item is None
    
def test_remove_item_nonexistent_does_nothing():
    collection = Collection(name="test")
    service = make_service()
    
    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        2,
    )
    
    service.remove_item(collection, "Does Not Exist", "cigar", 1)
    
    item = get_item_by_name(collection, "Padron x000")
    
    assert item.quantity == 2
    
def test_summary_by_category():
    collection = Collection(name="test")
        
    service = make_service()
        
    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        1,
    )
        
    collection = service.add_item(
        collection,
        "Theo",
        "Lab",
        1,
    )
        
    collection = service.add_item(
        collection,
        "Bowie",
        "Aussie",
        1,
    )
    
    summary = service.summary_by_category(collection)
    
    assert summary == {
        "Yorkie": 1,
        "Lab": 1,
        "Aussie": 1,
    }
    
def test_summary_by_category_adds_quantities():
    collection = Collection(name="test")
    service = make_service()
    
    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        1,
    )
    
    collection = service.add_item(
        collection,
        "Manny",
        "Yorkie",
        1,
    )
    
    collection = service.add_item(
        collection,
        "Theo",
        "Lab",
        1,
    )
    
    summary = service.summary_by_category(collection)
    
    assert summary == {
        "Yorkie": 2,
        "Lab": 1,
    }
    
def test_summary_by_category_empty_collection():
    collection = Collection(name="test")
    service = make_service()
    
    assert service.summary_by_category(collection) == {}
    
def test_add_remove_are_case_insensitive():
    collection = Collection(name="test")
    service = make_service()
    
    collection = service.add_item(
        collection, 
        "     Padron X000 ", 
        " CIGAR ",
        2,
    )
    
    collection = service.remove_item(
        collection,
        "padron x000",
        "cigar",
        1,
    )
    
    item = get_item_by_name(collection, "padron x000")
    assert item.quantity == 1
    