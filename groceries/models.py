from dataclasses import asdict, dataclass

@dataclass
class ShoppingListEntry:
    name: str
    quantity: int
    product_id: str = None

    def serialize(self):
        return asdict(self)