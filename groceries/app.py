from datetime import datetime
from groceries import list_maker
from groceries import shopper


def main():
    shopping_list = list_maker.get_grocery_list(datetime.today().strftime("%m-%d-%Y"))
    for list_entry in shopping_list:
        print(f"Looking for {list_entry}")
        shopper.find_food(list_entry)


main()
