from pages.commands_pair import CommandsPair
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from main.utils.data.config_manager import ConfigManager
models_list = []

BrowserUtils.init_the_driver()
for game in ConfigManager.get_config_data().base_URL:
    BrowserUtils.get_url(game)
    commands_pair = CommandsPair()
    commands_pair.wait_page_is_visible()
    models_list.append(DataUtils.game_dict_to_model(DataUtils.game_list_to_dict(commands_pair.get_date_time_rates())))