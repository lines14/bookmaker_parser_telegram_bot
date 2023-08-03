from pages.commands_pair_page import CommandsPairPage
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from main.utils.markup.HTML_utils import HTMLUtils
from main.utils.DB.database_utils import DatabaseUtils

class Parser:
    @staticmethod
    async def get_pair_info(state):
        global game_models_list
        game_models_list = []
        async with state.proxy() as data:
            global summary_links_model
            summary_links_model = DataUtils.dict_to_model(data.as_dict())
            BrowserUtils.init_the_driver()
            for link in summary_links_model.links:
                BrowserUtils.get_url(link)
                commands_pair_page = CommandsPairPage()
                commands_pair_page.wait_page_is_visible()
                game_models_list.append(DataUtils.dict_to_model(DataUtils.list_to_dict(commands_pair_page.get_date_time_rates())))

            for game in game_models_list:
                DatabaseUtils.sql_add_original_name(game.game.teams.firstTeam.name)
                DatabaseUtils.sql_add_original_name(game.game.teams.secondTeam.name)
                
            BrowserUtils.quit_driver()

    @staticmethod
    async def generate_picture():
        HTMLUtils.generate_HTML(summary_links_model.tournament_name, game_models_list)
        HTMLUtils.HTML_to_jpg()