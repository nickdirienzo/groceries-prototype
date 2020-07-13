from dataclasses import asdict, dataclass


@dataclass
class ShoppingListEntry:
    name: str
    group_name: str
    amount: int
    # Amazon product ID.
    plu: str = None

    def serialize(self):
        return asdict(self)
