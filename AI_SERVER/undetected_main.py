from undetected_chromedriver import Chrome, ChromeOptions
import time
import random
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Set up ChromeOptions
options = ChromeOptions()
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36')

# Use real user profile
options.add_argument(f"user-data-dir=/Users/ilya/PycharmProjects/AI_SERVER/1")

# Initialize driver
driver = Chrome(options=options)

# Manipulate navigator.webdriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# Navigate to the target website
driver.get('https://chatgpt.com')

text_field = driver.find_element(By.ID, "prompt-textarea")

# Interact with the text field
text_field.send_keys("Hello, ChatGPT!")

wait = WebDriverWait(driver, 10)
button = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='send-button']")))
button.click()

while True:
    e = input("> ")
    try:
        exec(e)
    except Exception as ex:
        traceback.print_exc()



# Close the driver and stop the display
driver.quit()
