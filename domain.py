from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

@dataclass
class Item:
    id: UUID
    name: str
    category: str
    quantity: int
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    
@dataclass
class Collection:
    name: str
    items: list[Item] = field(default_factory=list)