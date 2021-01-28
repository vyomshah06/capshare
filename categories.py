import json

with open('quotes.json', encoding="utf8") as f:
   data = json.load(f)
        
categories = []

for i in data:
    categories.append(i['Category'])

list_set = set(categories)
unique_list = list(list_set)
unique_list[0] = 'others'
unique_list = unique_list[::-1]

f.close()

from models import Category

for x in unique_list:
    category = Category(category_name=x)
    category.save()

