import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

EMAIL = os.environ.get("GROCERIES_AMAZON_EMAIL")
PASSWORD = os.environ.get("GROCERIES_AMAZON_PASSWORD")

TIMEOUT = 10

options = webdriver.FirefoxOptions()
options.headless = False
driver = webdriver.Firefox(options=options)

def click(driver: webdriver.Firefox, element_id: str):
    element = WebDriverWait(driver, TIMEOUT).until(
        EC.presence_of_element_located((By.ID, element_id))
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
    driver.get("https://primenow.amazon.com")
    driver.close()
