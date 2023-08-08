from datetime import datetime
from rutimeparser import parse

a = ['25 апреля', '15 марта']
b = sorted(a, key=lambda element: int(datetime.strptime(str(parse(element)),'%Y-%m-%d').timestamp()))
print(b)

# a = ['25 апреля', '15 марта']
# b = list(map(lambda element: int(datetime.strptime(str(parse(element)),'%Y-%m-%d').timestamp()), a))
# b.sort()
# c = list(map(lambda element: parse(datetime.fromtimestamp(element).strftime('%Y-%m-%d')).strftime('%d %B'), b))
# print(c)