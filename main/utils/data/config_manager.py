import os
import json
from main.utils.data.data_utils import DataUtils
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class ConfigManager:
    with open('../../../resources/config_data.json', 'r', encoding='utf-8') as data:
        config_data = DataUtils.dict_to_model(json.loads(data.read()))
        
    @classmethod
    def set_names_length(cls, length):
        def dict_filter(pair):
            key, value = pair
            if '__' in key:
                return False
            else:
                return True
        
        config_data = cls.config_data
        config_data.names_length = length
        new_data = dict(filter(dict_filter, (dict(vars(config_data))).items()))
        with open('../../../resources/config_data.json', 'w', encoding='utf-8') as data:
            json.dump(new_data, data, ensure_ascii=False, indent=4)