"""Idk what else to call this. They make the grocery list."""
import os
from collections import namedtuple

import yaml

GROCERIES_CONFIG = os.environ.get("GROCERIES_CONFIG")

ShoppingListEntry = namedtuple("ShoppingListEntry", ["name", "quantity"])

with open(GROCERIES_CONFIG) as _file:
    possible_groceries = yaml.full_load(_file)

def get_grocery_list():
    grocery_list = []
    for group, group_config in possible_groceries.items():
        food_options = [
            ShoppingListEntry(name, quantity)
            for name, quantity in group_config["foods"].items()
        ]
        cadence = group_config["cadence"]
        grocery_list.append(food_options[0])
    return grocery_list