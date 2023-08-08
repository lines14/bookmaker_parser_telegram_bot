a = [{'date': '1', 'body': 'Первый раз'}, {'date': '1', 'body': 'Первый два'}, {'date': '2', 'body': 'Второй раз'}, {'date': '2', 'body': 'Второй два'}]



for i in a:
    locals()[f'{list(i.keys())[0]}{list(i.values())[0]}'] = []