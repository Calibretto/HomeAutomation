#! /usr/bin/python3

import argparse
import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

from smbclient import open_file

# Constants & config
EAST_REN_BINS_URL = "https://www.eastrenfrewshire.gov.uk/bin-days"
POST_CODE_ELEMENT_NAME = "RESIDUALWASTEV2_PAGE1_POSTCODE"
SUBMIT_BUTTON_ELEMENT_NAME = "RESIDUALWASTEV2_FORMACTION_NEXT"
ADDRESS_SELECT_XPATH = "//select[@id='RESIDUALWASTEV2_PAGE2_UPRN']"
BIN_COLOUR_XPATH = "//span[@class='binColour']"
BINS_CLASS = "bins"
DUE_DATE_CLASS = "dueDate"
DUE_DAY_CLASS = "dueDay"

# argparse
parser = argparse.ArgumentParser(description='East Renfrewshire Bins Schedule')
parser.add_argument('browser', type=str, help='Browser to use', choices=['safari', 'chrome', 'firefox'])
parser.add_argument('post_code', type=str, help='Post Code to use')
parser.add_argument('address', type=str, help='Address to use')
parser.add_argument('--output', type=str, help='Output file location', default='./bins.json')
parser.add_argument('--username', type=str, help='Output file location username', required=False)
parser.add_argument('--password', type=str, help='Output file location password', required=False)

args = parser.parse_args()

# set up driver and load URL
def create_browser(browser):
    if browser == 'safari':
        return webdriver.Safari()
    elif browser == 'firefox':
        return webdriver.Firefox()
    elif browser == 'chrome':
        return webdriver.Chrome()
    
    return None

driver = create_browser(args.browser)
if driver is None:
    print('Invalid browser: ' + args.browser)
    exit(1)

driver.get(EAST_REN_BINS_URL)
driver.implicitly_wait(0.5)

# Enter post code and submit
post_code = driver.find_element(by=By.NAME, value=POST_CODE_ELEMENT_NAME)
post_code.send_keys(args.post_code)

submit_button = driver.find_element(by=By.NAME, value=SUBMIT_BUTTON_ELEMENT_NAME)
submit_button.click()

# Wait for form to submit
# TODO: Find a better way to handle this.
time.sleep(5)

# Wait for address select box to appear, select option and submit
address_element = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, ADDRESS_SELECT_XPATH)))
address_select = Select(address_element)
address_select.select_by_visible_text(args.address)

submit_button = driver.find_element(by=By.NAME, value=SUBMIT_BUTTON_ELEMENT_NAME)
submit_button.click()

# Wait for form to submit
# TODO: Find a better way to handle this.
time.sleep(5)

# Wait for bins data to load
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, BINS_CLASS)))

due_date = driver.find_element(By.CLASS_NAME, DUE_DATE_CLASS).text
due_day = driver.find_element(By.CLASS_NAME, DUE_DAY_CLASS).text

due = due_day + " " + due_date
print(due)

bin_colours = driver.find_elements(By.XPATH, BIN_COLOUR_XPATH)
for colour in bin_colours:
    print(colour.text)

bins = {'due': due, 'bins': [b.text for b in bin_colours]}
if args.output.startswith("smb://"):
    with open_file(args.output.strip('smb:'), mode="w", username=args.username, password=args.password) as file:
        file.write(json.dumps(bins))
else:
    with open(args.output, "w") as file:
        file.write(json.dumps(bins))

# End
driver.quit()