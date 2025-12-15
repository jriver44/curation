from domain import Collection
from services import CollectionService


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


def test_add_item_reject_zero_negative_quantity():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        0,
    )

    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        -1,
    )

    assert collection.items == []

    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        1,
    )

    assert len(collection.items) == 1


def test_add_item_rejects_blank_name_or_category():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "       ",
        "cigar",
        1,
    )

    collection = service.add_item(
        collection,
        "Padron",
        "       ",
        1,
    )

    assert collection.items == []


def test_add_item_merges_case_insensitive_but_preserves_display():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "   Padron X000 ",
        "   CIGAR   ",
        2,
    )

    collection = service.add_item(
        collection,
        "padron x000",
        "cigar",
        3,
    )

    assert len(collection.items) == 1
    assert collection.items[0].quantity == 5
    assert collection.items[0].name == "Padron X000"
    assert collection.items[0].category == "CIGAR" or collection.items[0].category == "Cigar"


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


def test_remove_item_zero_negative():
    collection = Collection(name="test")
    service = make_service()

    collection = service.remove_item(
        collection,
        "Teddy",
        "Yorkie",
        -1,
    )

    collection = service.remove_item(collection, "Teddy", "Yorkie", 0)

    assert collection.items == []

    collection = service.add_item(
        collection,
        "Teddy",
        "Yorkie",
        1,
    )

    assert len(collection.items) == 1

    collection = service.remove_item(
        collection,
        "Teddy",
        "Yorkie",
        1,
    )

    assert collection.items == []


def test_remove_item_wrong_category_does_nothing():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        2,
    )

    collection = service.remove_item(
        collection,
        "Padron x000",
        "tea",
        1,
    )

    assert get_item_by_name(collection, "Padron x000").quantity == 2


def test_remove_item_rejects_zero_or_negative():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        2,
    )

    collection = service.remove_item(
        collection,
        "Padron x000",
        "cigar",
        0,
    )

    collection = service.remove_item(
        collection,
        "Padron x000",
        "cigar",
        -1,
    )

    assert get_item_by_name(collection, "Padron x000").quantity == 2


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


def test_search_case_insensitive_and_substring():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Padron 1964 Anniversary",
        "cigar",
        1,
    )

    collection = service.add_item(
        collection,
        "Arturo Fuente OpusX",
        "cigar",
        1,
    )

    results = service.search(collection, "pAdRoN")

    assert [i.name for i in results] == ["Padron 1964 Anniversary"]


def test_search_trim_keyword_whitespace():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        1,
    )

    results = service.search(collection, "  padron  ")

    assert len(results) == 1
    assert results[0].name == "Padron x000"


def test_search_empty_keyword_returns_empty_list():
    collection = Collection(name="test")
    service = make_service()

    collection = service.add_item(
        collection,
        "Padron x000",
        "cigar",
        1,
    )

    assert service.search(collection, "") == []
    assert service.search(collection, "     ") == []
