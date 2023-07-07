from pages.commands_pair import CommandsPair
from main.driver.browser_utils import BrowserUtils
from main.utils.data.config_manager import ConfigManager

BrowserUtils.init_the_driver()
for match in ConfigManager.get_config_data().base_URL:
    BrowserUtils.get_url(match)
    commands_pair = CommandsPair()
    commands_pair.wait_page_is_visible()
    print(commands_pair.get_date_time_rates())