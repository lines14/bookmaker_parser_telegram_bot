import classutilities
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from main.utils.data.config_manager import ConfigManager

class BrowserFactory(classutilities.ClassPropertiesMixin):
    __instance = None

    @classmethod
    def init_instance(cls):
        if (cls.__instance is None):
            if (ConfigManager.get_config_data().browser == 'chrome'):
                options = webdriver.ChromeOptions()
                if (ConfigManager.get_config_data().is_headless):
                    options.add_argument('--no-sandbox')
                    # options.add_argument('--headless=new')
                    options.add_argument('--headless')
                    options.add_argument('--disable-gpu')
                    options.add_argument('--disable-software-rasterizer')
                    options.add_argument('--disable-setuid-sandbox')
                    options.add_argument('--disable-dev-shm-usage')
                    options.add_argument('--remote-debugging-address=0.0.0.0')
                    options.add_argument('--remote-debugging-port=9222')

                if (ConfigManager.get_config_data().locale):
                    browser_locale = ConfigManager.get_config_data().locale
                    options.add_argument('--lang={}'.format(browser_locale))
                
                options.add_argument('--incognito')
                if (ConfigManager.get_config_data().is_chromium):
                    options.BinaryLocation = '/home/userz/.local/bin/usr/bin/chromium-browser'
                    service = Service(executable_path='/home/userz/.local/bin/usr/bin/chromedriver')
                    cls.__instance = webdriver.Chrome(service=service, options=options)
                else:
                    cls.__instance = webdriver.Chrome(options=options)
                
                if (ConfigManager.get_config_data().is_maximize):
                    cls.__instance.maximize_window()

                if (ConfigManager.get_config_data().timeout):
                    cls.__instance.set_page_load_timeout(ConfigManager.get_config_data().timeout)

            elif (ConfigManager.get_config_data().browser == 'firefox'):
                options = webdriver.FirefoxOptions()
                options.add_argument('-private')
                if (ConfigManager.get_config_data().is_headless):
                    options.add_argument('--headless=new')
                    options.add_argument('--disable-gpu')

                if (ConfigManager.get_config_data().locale):
                    browser_locale = ConfigManager.get_config_data().locale
                    options.add_argument('--lang={}'.format(browser_locale))

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