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
    def game_dict_to_model(cls, dict):
        return json.loads(dict, object_hook=cls.nested_data_to_models)
    
    @classmethod
    def game_list_to_dict(cls, game_list):
        json_tmp = JsonTemplates()
        json_tmp.load('../../../resources/template.json')
        # if len(game_list) == 6:
        #     game_dict = {
        #         "first_name": f"{game_list[0]}",
        #         "first_rate": f"{game_list[1]}",
        #         "draw_rate": None,
        #         "second_name": f"{game_list[2]}",
        #         "second_rate": f"{game_list[3]}",
        #         "date": f"{game_list[4]}",
        #         "time": f"{game_list[5]}",
        #     }
        # elif len(game_list) == 8:
        #     game_dict = {
        #         "first_name": f"{game_list[0]}",
        #         "first_rate": f"{game_list[1]}",
        #         "draw_rate": f"{game_list[3]}",
        #         "second_name": f"{game_list[4]}",
        #         "second_rate": f"{game_list[5]}",
        #         "date": f"{game_list[6]}",
        #         "time": f"{game_list[7]}",
        #     }
        # else:
        #     print('parsed list not matches json scheme!')

        game_dict = {
            "first_name": f"{game_list[0]}",
            "first_rate": f"{game_list[1]}",
            "draw_rate": f"{game_list[3]}",
            "second_name": f"{game_list[4]}",
            "second_rate": f"{game_list[5]}",
            "date": f"{game_list[6]}",
            "time": f"{game_list[7]}",
            "first_logo": f"{game_list[8]}",
            "first_logo": f"{game_list[9]}",
        }
            
        print(game_dict)
        return json.dumps(json_tmp.generate(game_dict)[1], ensure_ascii=False)

        # with open('../../../resources/game.json', 'w', encoding='utf-8') as f:
        #     json.dump(data[1], f, ensure_ascii=False, indent=4)