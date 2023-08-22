import os
import time
from selenium.webdriver.remote.webdriver import WebDriver as root_driv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
# from dotenv import load_dotenv
from enum import Enum
from utils import wait_between

# load_dotenv()

DRIVER_PATH = r'chromedriver'

LINKEDIN_URL = f"""https://www.linkedin.com"""
LINKEDIN_FEED_URL = f"""{LINKEDIN_URL}/feed"""
LINKEDIN_CONNECTION_LIST_URL = (
    f"""{LINKEDIN_URL}/mynetwork/invite-connect/connections/"""
)


url1 = "https://www.linkedin.com/search/results/people/?origin=SWITCH_SEARCH_VERTICAL&sid=*(u"


WAIT_TIME_FOR_ELEMENT_LOAD = 20
MAX_RETRY = 3


class ChromeOptions(Enum):
    AVOID_CSS = "--blink-settings=CSSImagesEnabled=false"
    AVOID_JS = "--disable-javascript"
    AVOID_PLUGINS = "--blink-settings=pluginsEnabled=false"
    AVOID_MEDIA = "--blink-settings=imagesEnabled=false"
    AVOID_EXTENSIONS = "--disable-extensions"
    AVOID_GPU = "--disable-gpu"
    AVOID_SANDBOX = "--no-sandbox"
    HEADLESS = "--headless"


def _load_chrome_driver(
    driver_path,
    options=[
        ChromeOptions.AVOID_CSS,
        ChromeOptions.AVOID_MEDIA,
    ],
):
    if options is None:
        options = set()

    chrome_options = webdriver.ChromeOptions()
    for option in options:
        chrome_options.add_argument(option.value)

    # service = Service(executable_path=driver_path)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    driver = webdriver.Firefox()
    driver.implicitly_wait(WAIT_TIME_FOR_ELEMENT_LOAD)
    return driver


def wait_and_retry(func):
    def wrapper(*args, **kwargs):
        retry = 0
        max_retry = (
            kwargs.get("MAX_RETRY")
            if kwargs.get("MAX_RETRY") is not None
            else MAX_RETRY
        )
        MIN_WAIT_TIME = (
            kwargs.get("MIN_WAIT_TIME")
            if kwargs.get("MIN_WAIT_TIME") is not None
            else 1
        )
        MAX_WAIT_TIME = (
            kwargs.get("MAX_WAIT_TIME")
            if kwargs.get("MAX_WAIT_TIME") is not None
            else WAIT_TIME_FOR_ELEMENT_LOAD
        )
        while max_retry > retry:
            try:
                wait_between(1, 5)
                return func(*args, **kwargs)
            except NoSuchElementException as e:
                w = wait_between(MIN_WAIT_TIME, MAX_WAIT_TIME)
                print(f"Funtion '{func}':Waiting for {w}: Try {retry}\n")
                retry += 1
        raise Exception(f"Retry exceed... for function :'{func}'")

    return wrapper


@wait_and_retry
def login_to_linkedidn(user: str, pass_: str) -> root_driv:
    """
    Max Time :8+ sec
    """
    driver = _load_chrome_driver(DRIVER_PATH)
    driver.get(LINKEDIN_URL)
    username = driver.find_element(By.XPATH, '//*[@id="session_key"]')
    password = driver.find_element(By.XPATH, '//*[@id="session_password"]')
    signin_button = driver.find_element(
        By.XPATH,
        '//*[@id="main-content"]/section[1]/div/div/form[1]/div[2]/button',
    )
    username.send_keys(user)
    wait_between(1, 3)
    password.send_keys(pass_)
    wait_between(1, 3)
    signin_button.click()

    return driver


@wait_and_retry
def send_message(message: str, driver: root_driv):
    driver.get(LINKEDIN_CONNECTION_LIST_URL)
    print("redirect successful")
    wait_between(10, 15)
    connection_list = driver.find_elements(
        By.XPATH, '//*[@class="mn-connection-card artdeco-list"]/div[2]/div[1]/ul'
    )
    for connection in connection_list:
        # connection.click()
        name = connection.find_element(By.XPATH, "//span[2]")
        print(name)
    pass


@wait_and_retry
def send_message_to_connection(message: str, driver: root_driv):
    driver.get(url1)
    print("redirect successful")
    wait_between(2, 5)
    all_buttons = driver.find_elements(By.TAG_NAME, "button")
    message_buttons = [btn for btn in all_buttons if btn.text == "Message"]

    message_buttons[0].click()
    
    main_div = driver.find_element(By.XPATH, "//div[starts-with(@class, 'msg-form__msg-content-container')]")
    
    main_div.click()
    
    paragraphs = driver.find_elements(By.TAG_NAME, "p")
    
    paragraphs[-5].send_keys(message)

    submit = driver.find_element(By.XPATH, "//button[@type='submit']")
    submit.click()
    wait_between(2, 4)
    
    close_button = driver.find_element(By.XPATH, "//button[starts-with(@data-control-name, 'overlay.close_conversation_window')]")

    close_button.click()

def main():
    user = 'narayan.idstats@gmail.com'
    pass_ = '1999@Kapil'
    print(user, pass_)
    driver = login_to_linkedidn(user, pass_)
    print("login successful")
    # driver.get(LINKEDIN_FEED_URL)
    wait_between(10, 15)
    send_message_to_connection("test", driver=driver)


if __name__ == "__main__":
    main()
