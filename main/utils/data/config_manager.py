import os
import json
os.chdir(os.path.dirname(os.path.abspath(__file__)))

class ConfigManager:
    @staticmethod
    def get_config_data():
        with open('../../../resources/config_data.json', 'r', encoding='utf-8') as data:
            return type("ConfigData", (object, ), json.loads(data.read()))
        
    @classmethod
    def set_names_length(cls, length):
        def dict_filter(pair):
            key, value = pair
            if '__' in key:
                return False
            else:
                return True
        
        config_data = cls.get_config_data()
        config_data.names_length = length
        new_data = dict(filter(dict_filter, (dict(vars(config_data))).items()))
        with open('../../../resources/config_data.json', 'w', encoding='utf-8') as data:
            json.dump(new_data, data, ensure_ascii=False, indent=4)