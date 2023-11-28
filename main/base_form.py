from main.utils.log.logger import Logger
from selenium.webdriver.common.by import By
from main.utils.wait.wait_utils import WaitUtils
from main.driver.browser_factory import BrowserFactory

class BaseForm:
    def __init__(self, page_locator, page_name):
        self.page_locator = page_locator
        self.page_name = page_name

    def get_unique_element(self):
        WaitUtils.wait_element_located(self.page_locator)
        return BrowserFactory.instance.find_element(By.XPATH, self.page_locator)

    def page_is_displayed(self):
        Logger.log(f'    ▶ {self.page_name} is open')
        return (self.get_unique_element()).is_displayed()

    def page_is_enabled(self):
        Logger.log(f'    ▶ {self.page_name} is enabled')
        return (self.get_unique_element()).is_enabled()
    
    def wait_page_is_visible(self):
        WaitUtils.wait_element_visible(self.page_locator)
        print('got the page')
    
    def wait_page_is_clickable(self):
        WaitUtils.wait_element_clickable(self.page_locator)