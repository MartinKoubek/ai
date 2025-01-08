import os
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Path to your ChromeDriver
chromedriver_path = r"C:\Users\mkoubek\Downloads\chromedriver-win32\chromedriver-win32\chromedriver.exe"



# Set up the WebDriver to connect to an already opened Chrome browser
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=chrome_options)


def store_bug(bug):

    # Connect to the existing Chrome session
    print("Connected to the existing Chrome browser session.")

    # Interact with the already opened browser
    # Example: Open a webpage
    try:
        driver.get(f"https://bug.oraclecorp.com/pls/bug/webbug_edit.edit_info_top?rptno={bug}")

        # Wait until the page is fully loaded by checking the document readiness state
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')

        # Wait until the frame named 'bugframe' is available and switch to it
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "bugframe")))
        a = driver.find_element(By.TAG_NAME, "body").text + "\n\n"
        print("bugframe content loaded.")

        # Switch to the frame with ID 'BCIFRAME'
        WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.ID, "BCIFRAME")))
        time.sleep(5)
        combined_text = driver.title.strip() + "\n\n" + driver.find_element(By.TAG_NAME, "body").text + "\n\n"
    except Exception as e:
        print(f"Not able to load {bug}")
        return False

    print("BCIFRAME content added.")

    # Get the page title and sanitize it for use as a file name
    page_title = driver.title.strip().split('-')[0].strip().lower()

    # Save the combined content to a single HTML file
    with open(f"{bug}.txt", "w", encoding="utf-8") as file:
        file.write(combined_text)
    print(f"Saved to '{bug}.txt'.")
    return True

if __name__ == "__main__":
    data = pd.read_csv(r'C:\Users\mkoubek\Downloads\Bug_Report_1736266702057.csv')
    bugs = data['Num'].tolist()
    for bug in bugs:
        store_bug(str(bug))


