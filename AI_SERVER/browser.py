import os
import subprocess
import tempfile
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import threading

class Chrome:

    def __init__(self, h=False, dir=False, custom_driver=None, user_data_dir=None):
        self.driver_path = custom_driver or os.path.abspath("chromedriver")
        self.user_data_dir = user_data_dir or (tempfile.mkdtemp() if dir else "/Users/ilya/Library/Application Support/Google/Chrome/Default")
        self.chrome_options = Options()
        self.driver = None

        if h:
            self.chrome_options.add_argument("--headless")
            self.chrome_options.add_argument("--window-size=1920x1080")
            self.chrome_options.add_argument("--no-sandbox")
            self.chrome_options.add_argument("--disable-dev-shm-usage")
            self.chrome_options.add_argument("--disable-gpu")  # Disable GPU

        self.chrome_options.add_argument(f"user-data-dir={self.user_data_dir}")
        self.chrome_options.add_argument("--disable-blink-features=AutomationControlled")

        # Set up logging and capabilities
        capabilities = DesiredCapabilities.CHROME.copy()
        capabilities['goog:loggingPrefs'] = {'performance': 'ALL'}
        self.chrome_options.set_capability('goog:loggingPrefs', capabilities['goog:loggingPrefs'])

    def start(self):
        try:
            self.driver = webdriver.Chrome(service=Service(self.driver_path), options=self.chrome_options)
            return self.driver

        except Exception as e:
            print(f"Failed to start Chrome: {e}")
            return None