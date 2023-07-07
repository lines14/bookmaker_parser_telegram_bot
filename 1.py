import json
from main.utils.data.data_utils import DataUtils

data = '{"firstMatch": {"date": "1 июня", "time": "12:00", "rates": {"firstTeam": {"name": "Кек", "rate": 1.1}, "draw": {"rate": 0.5}, "secondTeam": {"name": "Кок", "rate": 2.1}}}}'
instance = json.loads(data, object_hook=DataUtils.nested_data_to_models)

try:
    if instance.firstMatch.rates.draw:
        print(instance.firstMatch.rates.firstTeam.rate)
except:
    print('Without draw')