import os
import time
from selenium.webdriver.remote.webdriver import WebDriver as root_driv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pickle

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

recruiter_url = "https://www.linkedin.com/talent/home"



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
    driver = webdriver.Chrome()
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

def get_otp():
  otp = input("Enter otp : ")
  return otp
 
 
@wait_and_retry
def is_verfication_code_page(driver: root_driv)->bool:
  h1 = driver.find_element(By.CLASS_NAME, 'content__header')
  if "Enter the code we've sent to phone number" in h1.text:
    return True
  return False

@wait_and_retry
def submit_verification_code(driver: root_driv):
  try:
    otp_input = driver.find_element(By.CLASS_NAME, 'input_verification_pin')
    otp_value = get_otp()
    otp_input.send_keys(otp_value)

    submit_button = driver.find_element(By.CLASS_NAME, "form__submit")
    wait_between(1, 2)
    submit_button.click()
    return True    
  except Exception as e:
    print("Exception in submit verification", e)
  return False
 
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


@wait_and_retry
def redirect_recuiter_page(driver: root_driv):
  driver.get(recruiter_url)
  return driver


@wait_and_retry
def is_choose_a_contract_page(driver: root_driv)->bool:
  try:
    h1 = driver.find_element(By.TAG_NAME, 'h1')
    if "Choose a contract" in h1.text:
      return True
  except Exception as e:
    print("Error in choose contract", e)
  return False


@wait_and_retry
def choose_a_contract(driver: root_driv):
  try:
    h3_elements = driver.find_elements(By.CLASS_NAME, "contract-list__item-summary-name")
    wait_between(1, 2)
    select_buttons = driver.find_elements(By.CLASS_NAME, "contract-list__item-buttons")
    wait_between(1, 2)
    for index, h3 in enumerate(h3_elements):
      print('Text ->', h3.text)
      if "Recruiter Lite" in h3.text:
        select_buttons[index].click()
        return True
  except Exception as e:
    print("Exception while choose a contract page", e)
  return False
      


@wait_and_retry
def search_people(name: str, driver: root_driv):
  search_box = driver.find_element(By.ID, 'system-search-typeahead')
  wait_between(1,2)
  search_box.send_keys(name)
  wait_between(2, 4)
  search_box.send_keys(Keys.RETURN)
  return  driver
  

@wait_and_retry
def send_mail(driver: root_driv, subject_text: str, message_text: str):
  message_buttons = driver.find_elements(By.XPATH, '//*[@data-live-test-component="message-icon-btn"]')
  
  
  for message_button in message_buttons:
    message_button.click()
    wait_between(1, 2)
    
    subject = driver.find_element(By.CLASS_NAME, "compose-subject__input")
    subject.send_keys(subject_text)    
    wait_between(1, 2)
    
    message = driver.find_element(By.CLASS_NAME, "compose-textarea__textarea")
    message.send_keys(message_text)
    
    wait_between(2, 4)
    send_button = driver.find_element(By.CLASS_NAME, "compose-actions__submit-button")
    # send_button.click()
    
    close = driver.find_element(By.CLASS_NAME, "inmail-component__button-tertiary-muted")
    close.click()
    break
    
  return driver



def main():
    user = ''
    pass_ = ''
    print(user, pass_)
    
    file_path = "driver.pickle"
    
    # Later, you can load the WebDriver instance back
    if os.path.exists(file_path):
      with open(file_path, "rb") as f:
        driver = pickle.load(f)
    else:
      driver = login_to_linkedidn(user, pass_)
      print("login successful")
      wait_between(10, 15)
      if is_verfication_code_page(driver):
        submit_verification_code(driver)    
      wait_between(3, 6)
      
      # Save the WebDriver instance using pickling
      with open(file_path, "wb") as f: 
        pickle.dump(driver, f)
    
    redirect_recuiter_page(driver)
    wait_between(1, 3)
    
    if is_choose_a_contract_page(driver):
      choose_a_contract(driver)
      
    wait_between(2, 4)
    search_people(name="Narayan Prajapat", driver=driver)
    wait_between(2, 4)
    send_mail(subject_text="Job opening", message_text="Openings", driver=driver)


if __name__ == "__main__":
    main()
