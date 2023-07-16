import classutilities
from selenium import webdriver
from main.utils.data.config_manager import ConfigManager

class BrowserFactory(classutilities.ClassPropertiesMixin):
    __instance = None

    @classmethod
    def init_instance(cls):
        if (cls.__instance is None):
            if (ConfigManager.get_config_data().browser == 'chrome'):
                options = webdriver.ChromeOptions()
                options.add_argument('--incognito')
                if (ConfigManager.get_config_data().is_headless):
                    options.add_argument("--headless=new")
                    options.add_argument('--disable-gpu')
                cls.__instance = webdriver.Chrome(options=options)

                if (ConfigManager.get_config_data().is_maximize):
                    cls.__instance.maximize_window()
                
                if (ConfigManager.get_config_data().timeout):
                    cls.__instance.set_page_load_timeout(ConfigManager.get_config_data().timeout)
                
                browser_locale = 'ru'
                options.add_argument("--lang={}".format(browser_locale))

            elif (ConfigManager.get_config_data().browser == 'firefox'):
                options = webdriver.FirefoxOptions()
                options.add_argument('-private')
                cls.__instance = webdriver.Firefox(options=options)

                if (ConfigManager.get_config_data().is_maximize):
                    cls.__instance.maximize_window()
                
                if (ConfigManager.get_config_data().timeout):
                    cls.__instance.set_page_load_timeout(ConfigManager.get_config_data().timeout)

    @classutilities.classproperty
    def instance(cls):
        return cls.__instance
        
    @instance.setter
    def instance(cls, value):
        cls.__instance = value