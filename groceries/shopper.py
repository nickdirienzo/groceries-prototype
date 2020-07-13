import os
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from groceries import models

EMAIL = os.environ.get("GROCERIES_AMAZON_EMAIL")
PASSWORD = os.environ.get("GROCERIES_AMAZON_PASSWORD")

TIMEOUT = 10

options = webdriver.FirefoxOptions()
options.headless = False
driver = None

NO_MORE_ITEMS = "Sorry, this item is no longer available."

def click(driver: webdriver.Firefox, lookup: str, by: By = By.ID):
    element = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((by, lookup))
    )
    element.click()


def send_keys(driver: webdriver.Firefox, element_id: str, keys: str):
    element = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    element.send_keys(keys)


def login():
    driver.get("https://amazon.com")
    # Click on sign in navbar item.
    click(driver, "nav-link-accountList")
    send_keys(driver, "ap_email", EMAIL)
    click(driver, "continue")
    send_keys(driver, "ap_password", PASSWORD)
    click(driver, "signInSubmit")


def _get_specific_food(list_entry: models.ShoppingListEntry):
    pass


def find_food(list_entry: models.ShoppingListEntry):
    # Lazily instantiate driver.
    driver = webdriver.Firefox(options=options)

    # If we've already logged in, let's not do it again.
    if not driver.get_cookies():
        login()

    if list_entry.product_id:
        return _get_specific_food(list_entry)

    url = "https://primenow.amazon.com/search?"
    query_params = {"keywords": list_entry.name, "rh": "p_95:A0D4"}
    driver.get(f"{url}{urlencode(query_params)}")

    click(driver, "//button[text()='Add']", by=By.XPATH)

    # Check to make sure we can add it to our cart.
    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, f"//div[text()='{NO_MORE_ITEMS}'"))
        )
        if element:
            print(f"Cannot add {list_entry}")
            return
    except TimeoutException:
        pass

    # If the modal doesn't show, it's already been added.
    # Don't wait too long.
    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "qtyFull"))
        )
    except TimeoutException:
        print("No need to enter more info.")
        return

    if element:
        # Modify this based on number of items or weight.
        send_keys(driver, "qtyFull", list_entry.quantity)

    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.ID, "qtyFraction"))
        )
    except TimeoutException:
        print("No fractional unit.")
        return

    if element:
        send_keys(driver, "qtyFraction", 0)

    click(driver, "//button[text()='Add to cart']", by=By.XPATH)

    import pdb; pdb.set_trace()
    return
