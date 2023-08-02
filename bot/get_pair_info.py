from pages.commands_pair import CommandsPair
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from main.utils.markup.HTML_utils import HTMLUtils

async def get_pair_info(state):
    models_list = []
    async with state.proxy() as data:
        BrowserUtils.init_the_driver()
        for game in data['games']:
            BrowserUtils.get_url(game)
            commands_pair = CommandsPair()
            commands_pair.wait_page_is_visible()
            models_list.append(DataUtils.dict_to_model(DataUtils.list_to_dict(commands_pair.get_date_time_rates())))

        HTMLUtils.generate_HTML(data['tournament_name'], models_list)
        HTMLUtils.HTML_to_jpg()
        BrowserUtils.quit_driver()