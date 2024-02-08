import time

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


options = Options()
options.headless = True

driver = webdriver.Chrome(options=options)
driver.get("https://www.olx.ua/uk/nedvizhimost/q-квартира/")


def write_to_sheet(data: list) -> None:
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
             "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)
    client = gspread.authorize(creds)

    sheet = client.open("flats").sheet1
    existing_headers = sheet.row_values(1)
    if existing_headers != ["Title", "Price", "Location", "Area"]:
        headers = ["Title", "Price", "Location", "Area"]
        sheet.append_row(headers)

    for item in data:
        sheet.append_row([item["title"], item["price"], item["location"], item["area"]])
        time.sleep(1)


def collect_data() -> None:
    wait = WebDriverWait(driver, 10)
    ads = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".css-1apmciz")))
    data = []
    for ad in ads:
        try:
            title = ad.find_element(By.CLASS_NAME, "css-16v5mdi").text
            price = ad.find_element(By.CLASS_NAME, "css-10b0gli").text
            location = ad.find_element(By.CLASS_NAME, "css-1a4brun").text.split(' - ')[0]
            area = ad.find_element(By.CLASS_NAME, "css-643j0o").text
            current_data = {
                "title": title,
                "price": price,
                "location": location,
                "area": area,
            }
            data.append(current_data)
        except NoSuchElementException:
            continue

    write_to_sheet(data)


try:
    while True:
        collect_data()
        next_page = driver.find_elements(By.CSS_SELECTOR, 'a[data-testid="pagination-forward"]')
        if next_page:
            next_page_url = next_page[0].get_attribute('href')
            driver.get(next_page_url)
        else:
            break
finally:
    driver.quit()
