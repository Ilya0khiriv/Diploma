import sys
import threading
import time

import requests
import json
import re
import os
from typing import Optional

lock = False



from browser import Chrome

from fastapi import FastAPI

app = FastAPI()

chrome1 = Chrome(custom_driver=os.path.abspath("chromedriver"), h=False, user_data_dir=os.path.abspath("chrome_profile"))
driver_ = chrome1.start()

driver_.get("https://chat.deepseek.com/")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/translate")
def read_item(text: str, cust_sys: str):
    ai = response(text_=text, cust_sys_=cust_sys)
    return {"cust_sys": cust_sys,
            "text": text,
            "ai": ai}



def response(text_=None, cust_sys_=None):
    from selenium.webdriver.common.by import By
    textarea = driver_.find_element(By.ID, "chat-input")
    textarea.click()

    text_blob = ((cust_sys_ + " " + text_).replace("\n", " "))

    # textarea.send_keys(text_blob)
    driver_.execute_script("arguments[0].value = arguments[1];", textarea, text_blob)
    textarea.send_keys(" ")
    textarea.send_keys("\n")

    elements = driver_.find_elements(By.CLASS_NAME, "ds-markdown--block")
    amount = len(elements)



    while True:
        time.sleep(1)
        new_elements = driver_.find_elements(By.CLASS_NAME, "ds-markdown--block")
        new_amount = len(new_elements)

        if amount != new_amount:
            while True:
                text_1 = new_elements[-1].text
                time.sleep(1)
                text_2 = new_elements[-1].text

                if text_1 != text_2:
                    continue
                return text_2.replace("\\", "").replace('"', '').replace("*", "")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8998)
