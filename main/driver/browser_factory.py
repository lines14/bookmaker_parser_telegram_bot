import classutilities
import undetected_chromedriver
from selenium import webdriver
from selenium_stealth import stealth
from main.utils.data.data_utils import DataUtils
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from main.utils.data.config_manager import ConfigManager

class BrowserFactory(classutilities.ClassPropertiesMixin):
    __instance = None

    @classmethod
    def init_instance(cls):
        if (cls.__instance is None):
            if (ConfigManager.config_data.browser == 'chrome'):
                options = webdriver.ChromeOptions()
                options.add_argument('--incognito')
                if (ConfigManager.config_data.is_headless):
                    options.add_argument('--no-sandbox')
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')

                if (ConfigManager.config_data.locale):
                    browser_locale = ConfigManager.config_data.locale
                    options.add_argument('--lang={}'.format(browser_locale))
                
                service = Service(executable_path=ChromeDriverManager().install())
                cls.__instance = undetected_chromedriver.Chrome(service=service, options=options)
                stealth(cls.__instance, **DataUtils.model_to_dict(ConfigManager.config_data.selenium_stealth))
                
                if (ConfigManager.config_data.is_maximize):
                    cls.__instance.maximize_window()

                if (ConfigManager.config_data.timeout):
                    cls.__instance.set_page_load_timeout(ConfigManager.config_data.timeout)

            elif (ConfigManager.config_data.browser == 'firefox'):
                options = webdriver.FirefoxOptions()
                options.add_argument('-private')
                if (ConfigManager.config_data.is_headless):
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')

                if (ConfigManager.config_data.locale):
                    browser_locale = ConfigManager.config_data.locale
                    options.add_argument('--lang={}'.format(browser_locale))

                cls.__instance = webdriver.Firefox(options=options)
                if (ConfigManager.config_data.is_maximize):
                    cls.__instance.maximize_window()
                    
                if (ConfigManager.config_data.timeout):
                    cls.__instance.set_page_load_timeout(ConfigManager.config_data.timeout)

    @classutilities.classproperty
    def instance(cls):
        return cls.__instance
        
    @instance.setter
    def instance(cls, value):
        cls.__instance = value