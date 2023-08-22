import requests
from time import sleep
import selenium.webdriver.support.ui as ui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from utils import wait_between


LINKEDIN_USER='narayanprajapat00099@gmail.com'
LINKEDIN_PASSWORD='Kapil@00099'


LINKEDIN_URL = f"""https://www.linkedin.com"""
LINKEDIN_FEED_URL = f"""{LINKEDIN_URL}/feed"""
LINKEDIN_CONNECTION_LIST_URL = (
    f"""{LINKEDIN_URL}/mynetwork/invite-connect/connections/"""
)


def main():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(
        executable_path=r'chromedriver', chrome_options=chrome_options
    )
    url = "https://www.linkedin.com/"
    driver.get(url=url)

    username = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    password = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    signin_button = driver.find_element(
        By.XPATH,
        '//*[@id="main-content"]/section[1]/div/div/form[1]/div[2]/button',
    )
    username.send_keys(LINKEDIN_USER)
    wait_between(1, 3)
    password.send_keys(LINKEDIN_PASSWORD)
    wait_between(1, 3)
    signin_button.click()
    sleep(30)
    
    
    
if __name__ == "__main__":
    main()