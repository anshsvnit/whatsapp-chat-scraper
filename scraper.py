"""
Importing the libraries that we are going to use
for loading the settings file and scraping the website
"""
import configparser
import time
import logging
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import pandas as pd
from selenium.webdriver.common.keys import Keys


def load_settings():
    """
    Loading and assigning global variables from our settings.txt file
    """
    config_parser = configparser.RawConfigParser()
    config_file_path = 'settings.txt'
    config_parser.read(config_file_path)

    browser = config_parser.get('config', 'BROWSER')
    browser_path = config_parser.get('config', 'BROWSER_PATH')
    name = config_parser.get('config', 'NAME')
    page = config_parser.get('config', 'PAGE')
    csv_location = config_parser.get('config', OUTPUT_FILE_LOCATION)

    settings = {
        'browser': browser,
        'browser_path': browser_path,
        'name': name,
        'page': page,
        'csv_location': csv_location
    }
    return settings


def load_driver(settings):
    """
    Load the Selenium driver depending on the browser
    (Edge and Safari are not running yet)
    """
    driver = None
    if settings['browser'] == 'firefox':
        firefox_profile = webdriver.FirefoxProfile(settings['browser_path'])
        driver = webdriver.Firefox(firefox_profile)
    elif settings['browser'] == 'chrome':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('user-data-dir=' +
                                    settings['browser_path'])
        driver = webdriver.Chrome(options=chrome_options)
    elif settings['browser'] == 'safari':
        pass
    elif settings['browser'] == 'edge':
        pass

    return driver


def search_chatter(driver, settings):
    """
    Function that search the specified user and activates his chat
    """

    while True:

        for chatter in driver.find_elements_by_xpath("//div[@class='_3TEwt']"):
            chatter_name = chatter.text
            print(chatter_name)
            if settings['name'] in chatter_name:
                chatter.click()
                return


def read_last_in_message(driver, message_limit):
    """
    Reading the last message that you got in from the chatter
    """

    curr_messages = []
    first_msg = ""
    curr_msg_list = driver.find_elements_by_xpath("//div[contains(@class,'focusable-list-item')]")
    for elem in curr_msg_list:
        try:
            msg_info = dict()

            message_container = elem.find_element_by_xpath(".//div[contains(@class,'copyable-text')]")
            message = message_container.find_element_by_xpath(
                ".//span[contains(@class,'selectable-text invisible-space copyable-text')]"
            ).text
            if first_msg == "":
                first_msg = message

            if message_limit == message:
                break
            msg_info['message'] = message

            time_container = elem.find_element_by_xpath(".//div[@class='_2f-RV']")
            t = time_container.find_element_by_xpath(".//span[@class='_3EFt_']")
            msg_info['time'] = t.text

            try:
                sender_container = elem.find_element_by_xpath(".//div[contains(@class,'_2lc14')]")
                sender = sender_container.find_element_by_xpath(".//span[@class='_2a1Yw _1OmDL _3FXB1']")
                msg_info['sender'] = sender.text
            except:
                logging.info("no sender")
                curr_messages.append(msg_info)
                continue
            curr_messages.append(msg_info)

        except (NoSuchElementException, StaleElementReferenceException):  # In case there are only emojis in the message
            try:
                date_elem = elem.find_element_by_xpath(".//span[@class='_3FXB1']")
                date_text = date_elem.text
                curr_messages.append({'date': date_text})
                continue
            except:
                continue

    return curr_messages, first_msg


def main():
    """
    Loading all the configuration and opening the website
    (Browser profile where whatsapp web is already scanned)
    """
    settings = load_settings()
    driver = load_driver(settings)
    driver.get(settings['page'])

    # search_chatter(driver, settings)
    input("Scan whatsapp QR code, select the message group and Press Enter to continue...")
    message_list, first_msg = read_last_in_message(driver, "")
    msg_store = pd.DataFrame(message_list)
    while True:
        message_list, first_msg = read_last_in_message(driver, first_msg)
        new_msgs = pd.DataFrame(message_list)
        msg_store = new_msgs.append(msg_store)
        msg_store.to_csv(settings['csv_location'])
        driver.find_element_by_xpath("//div[@class='_9tCEa']").send_keys(Keys.PAGE_UP)
        time.sleep(1)
        driver.find_element_by_xpath("//div[@class='_9tCEa']").send_keys(Keys.PAGE_UP)
        time.sleep(1)


if __name__ == '__main__':
    main()
