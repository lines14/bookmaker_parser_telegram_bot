from main.utils.data.data_utils import DataUtils
from main.utils.DB.database_utils import DatabaseUtils

class Modificator:
    async def check_original_name(name):
        return DatabaseUtils.sql_check_original_name(name)[0][0]
    
    async def get_short_name(name):
        return DatabaseUtils.sql_get_short_name(name)[0][0]
    
    async def add_short_name(state):
        async with state.proxy() as data:
            names_model = DataUtils.dict_to_model(data.as_dict())
            DatabaseUtils.sql_add_short_name(names_model.original_name, names_model.short_name)