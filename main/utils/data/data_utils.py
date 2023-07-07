import json
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