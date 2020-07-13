"""Idk what else to call this. They make the grocery list."""
import json
import os
import random

import yaml

from groceries import models

GROCERIES_CONFIG = os.environ.get("GROCERIES_CONFIG")
GROCERY_LIST_ARCHIVE = os.environ.get("GROCERIES_LIST_ARCHIVE")

with open(GROCERIES_CONFIG) as _file:
    possible_groceries = yaml.full_load(_file)


def get_grocery_list(dd_mm_yyyy: str):
    if os.path.isfile(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json")):
        with open(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json")) as _file:
            return [models.ShoppingListEntry(**e) for e in json.load(_file)]

    grocery_list = []
    for group, group_config in possible_groceries.items():
        food_options = {
            name: models.ShoppingListEntry(name, group_name=group, **food_option)
            for name, food_option in group_config["foods"].items()
        }

        cadence = group_config["cadence"]
        # TODO: Stuff with cadence.

        grocery_list.append(random.choice(iter(food_options.values())))

    # Save for history.
    with open(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json"), "w") as _file:
        _file.writelines(json.dumps([e.serialize() for e in grocery_list], indent=2))

    return grocery_list


def get_substitute(entry: models.ShoppingListEntry):
    food_options = possible_groceries[entry.group_name]["foods"]
    food_options.pop(entry.name, None)

    sub = next(iter(food_options.keys()))
    sub_entry = models.ShoppingListEntry(sub, entry.group_name, **food_options[sub])
    return sub_entry
    # # Resave the file.
    # new_list = []
    # with open(os.path.join(GROCERY_LIST_ARCHIVE, f"{dd_mm_yyyy}.json")) as _file:
    #     for e in json.load(_file):
    #         if e["name"] == entry.name:
    #             new_list.append(sub_entry)
    #         new_list.append(models.ShoppingListEntry(**e))
