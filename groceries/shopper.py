import os
from urllib.parse import urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

from groceries import list_maker
from groceries import models

EMAIL = os.environ.get("GROCERIES_AMAZON_EMAIL")
PASSWORD = os.environ.get("GROCERIES_AMAZON_PASSWORD")

TIMEOUT = 10

options = webdriver.FirefoxOptions()
options.headless = False
driver = webdriver.Firefox(options=options)

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


def find_select(driver: webdriver.Firefox, element_id: str):
    element = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, element_id))
    )
    return Select(element)


def login():
    driver.get("https://amazon.com")
    # Click on sign in navbar item.
    click(driver, "nav-link-accountList")
    send_keys(driver, "ap_email", EMAIL)
    click(driver, "continue")
    send_keys(driver, "ap_password", PASSWORD)
    click(driver, "signInSubmit")


def _get_specific_food(list_entry: models.ShoppingListEntry):
    url = driver.find_element_by_xpath(
        f"//a[contains(@href, '{list_entry.plu}')]"
    ).get_attribute("href")
    driver.get(url)

    WebDriverWait(driver, 2).until(
        EC.presence_of_element_located((By.ID, "availability"))
    )
    in_stock = driver.find_element_by_id("availability").text == "In Stock."
    if not in_stock:
        print(f"Cannot add {list_entry}")
        substitute = list_maker.get_substitute(list_entry)
        print(f"Attempting to sub with {substitute}")
        return find_food(substitute)

    qty_dropdown = None
    try:
        qty_dropdown = find_select(driver, "primenowQuantity")
        if qty_dropdown.first_selected_option.text != str(list_entry.amount):
            send_keys(driver, "primenowQuantity", list_entry.amount)
    except (TimeoutException, NoSuchElementException):
        pass

    # If that times out, let's try a different identifier.
    if qty_dropdown is None:
        qty_dropdown = find_select(driver, "primeNowVariableWeightWhole")
        if qty_dropdown.first_selected_option.text != str(list_entry.amount):
            send_keys(driver, "primeNowVariableWeightWhole", list_entry.amount)

    # TODO: Support fractions.
    try:
        send_keys(driver, "primeNowVariableWeightFraction", 0)
    except TimeoutException:
        pass

    click(driver, "add-to-cart-button")
    try:
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.ID, "primenow-atc-button-announce"))
        )
    except TimeoutException:
        print(f"Cannot add {list_entry} to the cart.")


def find_food(list_entry: models.ShoppingListEntry):
    # If we've already logged in, let's not do it again.
    if not driver.get_cookies():
        login()

    url = "https://primenow.amazon.com/search?"
    query_params = {"keywords": list_entry.name, "rh": "p_95:A0D4"}
    driver.get(f"{url}{urlencode(query_params)}")

    if list_entry.plu is not None:
        return _get_specific_food(list_entry)

    click(driver, "//button[text()='Add']", by=By.XPATH)

    # Check to make sure we can add it to our cart.
    try:
        element = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//div[text()='{NO_MORE_ITEMS}'")
            )
        )
        if element:
            print(f"Cannot add {list_entry}")
            substitute = list_maker.get_substitute(list_entry)
            print(f"Attempting to sub with {substitute}")
            return find_food(substitute)
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
        # TODO: Modify this based on number of items or weight.
        qty_dropdown = Select(driver.find_element_by_id("qtyFull"))
        if qty_dropdown.first_selected_option.text != str(list_entry.amount):
            send_keys(driver, "qtyFull", list_entry.amount)

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


def go_to_cart():
    driver.get("https://primenow.amazon.com/cart?ref_=pn_dp_nav_cart")
