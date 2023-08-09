import re
import json
from datetime import datetime
from rutimeparser import parse
from json_templates import JsonTemplates

class DataUtils:            
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
                elif '\n' in text:
                    splitted = text.split('\n')
                else:
                    splitted = text.split()
                trimmed = list(map(lambda element: re.sub('[,| |\n]', '', element), splitted))
                if 'https' in text:
                    return list(filter(lambda element: len(element) > 21, trimmed))
                else:
                    linked = list(map(lambda element: 'https://www.'+element, trimmed))
                    return list(filter(lambda element: len(element) > 21, linked))
            else:
                if len(text) > 21:
                    if 'https' in text:
                        return text
                    else:
                        return 'https://www.'+text
        elif text == 'Проверить названия!':
            return True
        else:
            return False

    @staticmethod
    def list_to_matrix_by_date(game_models_list):
        unix_sorted_game_models_list = sorted(game_models_list, key=lambda game: int(datetime.strptime(str(parse(game.date)),'%Y-%m-%d').timestamp()))
        date_dict = {}
        for item in unix_sorted_game_models_list:
            date = item.date
            if date not in date_dict:
                date_dict[date] = []
            date_dict[date].append(item)

        game_models_matrix = list(date_dict.values())
        return game_models_matrix