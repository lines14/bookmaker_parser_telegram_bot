from pages.commands_pair_page import CommandsPairPage
from main.driver.browser_utils import BrowserUtils
from main.utils.data.data_utils import DataUtils
from main.utils.markup.HTML_utils import HTMLUtils
from main.utils.data.config_manager import ConfigManager
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
                if not DatabaseUtils.sql_check_original_name(game.game.teams.firstTeam.name)[0][0]:
                    DatabaseUtils.sql_add_original_name(game.game.teams.firstTeam.name)
                if not DatabaseUtils.sql_check_original_name(game.game.teams.secondTeam.name)[0][0]:
                    DatabaseUtils.sql_add_original_name(game.game.teams.secondTeam.name)
            
            BrowserUtils.quit_driver()
        
    @staticmethod
    async def check_names_length():
        long_names_list = []
        for game in game_models_list:
            if len(game.game.teams.firstTeam.name) > ConfigManager.get_config_data().names_length and not DatabaseUtils.sql_get_short_name(game.game.teams.firstTeam.name)[0][0]:
                long_names_list.append(DataUtils.dict_to_model(game.game.teams.firstTeam.name))
            if len(game.game.teams.secondTeam.name) > ConfigManager.get_config_data().names_length and not DatabaseUtils.sql_get_short_name(game.game.teams.secondTeam.name)[0][0]:
                long_names_list.append(DataUtils.dict_to_model(game.game.teams.secondTeam.name))
        
        if long_names_list:
            return long_names_list
            
    @staticmethod
    async def add_short_names(state):
        async with state.proxy() as data:
            for mapped_names in list(data.items())[2:]:
                DatabaseUtils.sql_add_short_name(mapped_names[0], mapped_names[1])
            for game in game_models_list:
                first_team_short_name = DatabaseUtils.sql_get_short_name(game.game.teams.firstTeam.name)[0][0]
                second_team_short_name = DatabaseUtils.sql_get_short_name(game.game.teams.secondTeam.name)[0][0]
                if first_team_short_name:
                    game.game.teams.firstTeam.name = first_team_short_name
                if second_team_short_name:
                    game.game.teams.secondTeam.name = second_team_short_name


    @staticmethod
    async def generate_picture():
        HTMLUtils.generate_HTML(summary_links_model.competition_type, summary_links_model.tournament_name, game_models_list)
        HTMLUtils.HTML_to_jpg(ConfigManager.get_config_data().large_size)