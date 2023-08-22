import os
import time
import json
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

    service = Service(executable_path=driver_path)
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
  try:
    h1 = driver.find_element(By.CLASS_NAME, 'content__header')
    if "Enter the code we've sent to phone number" in h1.text:
      print("Verification page found")
      return True
  except NoSuchElementException as e:
    print("No such eleent found while find is verfication code", e)
  print("Verification page not found")
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
def send_mail(name:str, title:str, driver: root_driv, subject_text: str, message_text: str):
  message_buttons = driver.find_elements(By.XPATH, '//*[@data-live-test-component="message-icon-btn"]')
  
  
  for message_button in message_buttons:
    message_button.click()
    wait_between(1, 2)
    _name = driver.find_element(By.CLASS_NAME, "artdeco-entity-lockup__title")
    print(_name.text)
    _title = driver.find_element(By.CLASS_NAME, "artdeco-entity-lockup__subtitle")
    print(_title.text)
    is_title_match = title in _title.text
    is_name_match = name in _name.text
    
    if is_name_match and is_title_match:
      subject = driver.find_element(By.CLASS_NAME, "compose-subject__input")
      subject.send_keys(subject_text)    
      wait_between(1, 2)
      
      message = driver.find_element(By.CLASS_NAME, "compose-textarea__textarea")
      message.send_keys(message_text)
      
      wait_between(2, 4)
      send_button = driver.find_element(By.CLASS_NAME, "compose-actions__submit-button")
      # send_button.click()
      wait_between(2,4)
      close = driver.find_element(By.CLASS_NAME, "inmail-component__button-tertiary-muted")
      close.click()
      break
      
  return driver

@wait_and_retry
def check_talent_signup_page(driver: root_driv)-> bool:
  try:
    h1 = driver.find_element(By.TAG_NAME, 'h1')
    if "Sign in to LinkedIn Talent Solutions" not in h1.text:
      return False
  except NoSuchElementException as se:
    pass
  
  return True
  
  
@wait_and_retry
def login_into_talent_page(driver: root_driv, username:str, password:str):
  try:
    username_element = driver.find_element(By.ID, "username")
    username_element.send_keys(username)
    wait_between(1,2)
    password_element = driver.find_element(By.ID, "password")
    password_element.send_keys(password)
    wait_between(1,2)
    submit = driver.find_element(By.CLASS_NAME, "from__button--floating")
    submit.click()
  except Exception as e:
    pass

@wait_and_retry
def fetch_inbox_message_user(driver: root_driv, name: str):
  users = driver.find_elements(By.CLASS_NAME, "_conversation-card-title-row_z8knzq")
  
  for user in users:
    user_name = user.find_element(By.CLASS_NAME, "_conversation-card-participant-name_z8knzq")
    
    if name in user_name.text:
      user.click()
      return True
  return False
  
  


@wait_and_retry
def fetch_previous_chat(driver: root_driv):
  message_record_list = []
  message_container_list = driver.find_elements(By.CLASS_NAME,
  "_message-list-item_1gj1uc")
  
  for message_container in message_container_list:
    message_info = message_container.find_element(By.CLASS_NAME, "a11y-message-thread")
    name_and_date = message_info.find_element(By.CLASS_NAME, "_message-metadata_1gj1uc")
    
    message_name = name_and_date.find_element(By.CLASS_NAME, "_headingText_e3b563")
    
    message_date = name_and_date.find_element(By.CLASS_NAME, "_lineHeightOpen_1e5nen")
    
    message_value = message_info.find_element(By.CLASS_NAME, "_message-body_content_1gj1uc")

    # message_value = paragraph.find_element(By.XPATH, "//following-sibling::div")
    
    message_record = {
      "name": message_name.text, 
      "date": message_date.text, 
      "value": message_value.text
    }
    
    message_record_list.append(message_record)
    
  return message_record_list  


def main():
    user = 'ramon@intelatek.co'
    pass_ = 'HunterProSP'
    
    print(user, pass_)
    
    file_path = "driver.pickle"
    file_path1 = "ramon_driver_info.json"
    
    # Later, you can load the WebDriver instance back
    if os.path.exists(file_path1):
      # with open(file_path, "rb") as f:
      #   driver = pickle.load(f)
      with open(file_path1, "r") as f:
        loaded_driver_info = json.load(f)

      driver = webdriver.Chrome()
      driver.get(loaded_driver_info["current_url"])
      for cookie in loaded_driver_info["cookies"]:
        driver.add_cookie(cookie)
      
      
    else:
      driver = login_to_linkedidn(user, pass_)
      print("login successful")
      wait_between(10, 15)
      print("time end")
      if is_verfication_code_page(driver):
        submit_verification_code(driver)    
      wait_between(3, 6)
      print("Writing pickle file")
      
      driver_info = {
        "current_url": driver.current_url,
        "cookies": driver.get_cookies()
      }

      with open(file_path1, "w") as f:
        json.dump(driver_info, f)
      
      
      # Save the WebDriver instance using pickling
      # with open(file_path, "wb") as f: 
        # pickle.dump(driver, f)
    driver.get("https://www.linkedin.com/feed")
    redirect_recuiter_page(driver)
    wait_between(5, 10)
    
    if check_talent_signup_page(driver=driver):
      login_into_talent_page(driver=driver, username=user, password=pass_)
    
    
    if is_choose_a_contract_page(driver):
      choose_a_contract(driver)
      
    wait_between(2, 4)
    name = "Narayan Prajapat"
    search_people(name=name, driver=driver)
    wait_between(2, 4)
    
    
    
    driver.get("https://www.linkedin.com/talent/inbox/0/main")
    
    
    if fetch_inbox_message_user(driver=driver, name="Shailesh Pandit"):
      res = fetch_previous_chat(driver=driver)
      print(res)
    
    message_text = """
      Hii Narayan, I hope you are doing well. Let me know if you are open to new opportunities.
    """
    
    title = "SDE at SignalX.ai |ExIdeal"
    
    # send_mail(name=name, title=title,subject_text="Regarding New Opportunities", message_text=message_text, driver=driver)

    wait_between(300, 600)

if __name__ == "__main__":
    main()
