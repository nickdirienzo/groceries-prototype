"""Idk what else to call this. They make the grocery list."""
import json
import os
from collections import namedtuple

import yaml

GROCERIES_CONFIG = os.environ.get("GROCERIES_CONFIG")
GROCERY_LIST_ARCHIVE = os.environ.get("GROCERIES_LIST_ARCHIVE")

ShoppingListEntry = namedtuple("ShoppingListEntry", ["name", "quantity"])

with open(GROCERIES_CONFIG) as _file:
    possible_groceries = yaml.full_load(_file)


def get_grocery_list(dd_mm_yyyy: str):
    if os.path.isfile(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json")):
        with open(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json")) as _file:
            return json.load(_file)

    grocery_list = []
    for group, group_config in possible_groceries.items():
        food_options = [
            ShoppingListEntry(name, quantity)
            for name, quantity in group_config["foods"].items()
        ]
        cadence = group_config["cadence"]
        grocery_list.append(food_options[0])

    # Save for history.
    with open(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json"), "w") as _file:
        _file.writelines([json.dumps(grocery_list)])

    return grocery_list
