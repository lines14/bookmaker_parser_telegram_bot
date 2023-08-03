import re
import json
from json_templates import JsonTemplates
from main.utils.log.logger import Logger

class DataUtils:
    @staticmethod
    def is_JSON(API_response):
        try:
            result = json.loads(API_response)
            Logger.log('[info] ▶ api response is json')
            return type(result) == dict
        except:
            Logger.log('[error]▶ api response is not json!')
            return False
        
    @staticmethod
    def JSON_to_models(JSON_list):
        Logger.log('    ▶ get models from JSON')
        return list(map(lambda element: type("Model", (object, ), element), JSON_list))

    @staticmethod
    def data_to_models(parent_class, data_matrix, rows_count=1, counter=0):
        models_list = []
        if rows_count > 1:
            Logger.log('    ▶ get models from table')
        while counter < rows_count:
            model_fields = list(filter(lambda attr: not attr.startswith("__"), dir(parent_class)))
            model_dict = dict.fromkeys(model_fields)
            for key in model_dict:
                model_dict[key] = data_matrix[counter][model_fields.index(key)]
            model = type("Model", (object, ), model_dict)
            models_list.append(model)
            counter += 1

        return models_list
    
    @classmethod
    def nested_data_to_models(cls, dict):
        obj = cls()
        obj.__dict__.update(dict)
        return obj
    
    @classmethod
    def dict_to_model(cls, dict):
        return json.loads(json.dumps(dict, ensure_ascii=False), object_hook=cls.nested_data_to_models)
    
    @staticmethod
    def list_to_dict(game_list):
        json_tmp = JsonTemplates()
        json_tmp.load('../../../resources/game_schema.json')
        game_dict = {
            "first_name": f"{game_list[0]}",
            "first_rate": f"{game_list[1]}",
            "draw_rate": f"{game_list[3]}",
            "second_name": f"{game_list[4]}",
            "second_rate": f"{game_list[5]}",
            "date": f"{game_list[6]}",
            "time": f"{game_list[7]}",
            "first_logo": f"{game_list[8]}",
            "second_logo": f"{game_list[9]}",
        }
        
        return json_tmp.generate(game_dict)[1]
    
    @staticmethod
    def links_processing(text):
        if 'fonbet.kz' in text:
            if text.count('fonbet.kz') > 1:
                if ',' in text:
                    splitted = text.split(',')
                else:
                    splitted = text.split()
                trimmed = list(map(lambda element: re.sub('[,| ]', '', element), splitted))
                if 'https' in text:
                    return trimmed
                else:
                    return list(map(lambda element: 'https://www.'+element, trimmed))
            else:
                if 'https' in text:
                    return text
                else:
                    return 'https://www.'+text
        elif text == 'Сгенерировать!':
            return True
        else:
            return False