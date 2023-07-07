from main.utils.log.logger import Logger
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from main.utils.wait.wait_utils import WaitUtils
from main.driver.browser_factory import BrowserFactory

class BaseElement:
    def __init__(self, element_locator, element_name):
        self.element_locator = element_locator
        self.element_name = element_name

    def get_element(self):
        return BrowserFactory.instance.find_element(By.XPATH, self.element_locator)

    def get_elements(self):
        return BrowserFactory.instance.find_elements(By.XPATH, self.element_locator)

    def get_text(self):
        Logger.log(f'    ▶ get {self.element_name} text:')
        text = (self.get_element()).text
        Logger.log(f'    ▶ text contains: "{text}"')
        return text

    def click_button(self):
        Logger.log(f'    ▶ click {self.element_name}')
        (self.get_element()).click()

    def input_text(self, text):
        Logger.log(f'    ▶ input {self.element_name}')
        (self.get_element()).send_keys(text)

    def enter_text(self, text):
        Logger.log(f'    ▶ input {self.element_name} and submit')
        (self.get_element()).send_keys(text + Keys.ENTER)

    def get_attribute_value(self, attr):
        return (self.get_element()).get_attribute(attr)

    def element_is_displayed(self):
        Logger.log(f'    ▶ {self.element_name} is present')
        return (self.get_element()).is_displayed()

    def element_is_enabled(self):
        return (self.get_element()).is_enabled()

    def parse_elements_for_attr(self, attr):
        return list(map(lambda element: element.get_attribute(attr), self.get_elements()))

    def parse_elements_for_text(self):
        return list(map(lambda element: element.text, self.get_elements()))

    def wait_is_visible(self):
        Logger.log(f'    ▶ wait {self.element_name} is visible')
        WaitUtils.wait_element_visible(self.element_locator)

    def wait_staleness_of(self):
        WaitUtils.wait_element_staleness_of(self.element_locator)
    
    def wait_is_clickable(self):
        Logger.log(f'    ▶ wait {self.element_name} is clickable')
        WaitUtils.wait_element_clickable(self.element_locator)
        