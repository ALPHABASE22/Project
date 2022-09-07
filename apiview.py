import requests
from datetime import *
import json
from hashlib import sha256
from pprint import pprint

url="https://api.orderful.com/v2/transactions"
headers = { "orderful-api-key": 'eb94a56f4749458f9984c783fee7cb49'}
value=requests.get(url,headers=headers)
info=value.json()['data']
das=info[0]["message"]["transactionSets"][0]["N1_loop"]
# print(info[0]['message']['transactionSets'][0]['transactionSetHeader'][0]['transactionSetIdentifierCode'])
# pprint(info[4]['message'])
for i in range(len(info)):
    if info[i]['message']['transactionSets'][0]['transactionSetHeader'][0]['transactionSetIdentifierCode'] == '850':
        pprint(info[i])







# url="https://www.partytopics.com/rest/V1/orders"
# headers = {'Authorization': 'Bearer ' + "le3lo6hlnfjlumwpdvz6v906kfio7yjp"}
# from_date = datetime.today() - timedelta(days=7)
# from_date = from_date.strftime('%Y-%m-%d %H:%M:%S')
# params = {
#             'searchCriteria[filter_groups][0][filters][0][field]': 'status',
#             'searchCriteria[filter_groups][0][filters][0][value]': 'processing',
#             'searchCriteria[filter_groups][0][filters][0][condition_type]': 'eq',
#             'searchCriteria[filter_groups][1][filters][0][field]': 'created_at',
#             'searchCriteria[filter_groups][1][filters][0][value]': from_date,
#             'searchCriteria[filter_groups][1][filters][0][condition_type]': 'from',
#             'searchCriteria[page_size]': '200'
#             # 'searchCriteria[filter_groups][2][filters][0][field]': 'increment_id',
#             # 'searchCriteria[filter_groups][2][filters][0][value]': '100017085'
#         }
# data=requests.get(url,params=params,headers=headers)
# demo=data.json()
# pprint(demo)
# print(demo.keys())
# count=0
# for i in range(len(demo['items'])):
#     for j in range(len(demo['items'][i]['items'])):
#         value=demo['items'][i]['items'][j]['discount_amount']
#         if (value>0):
#             print(f"Item code for amount {value}:",demo['items'][i]['items'][j]['sku'])   
#         elif (value==0):
#             print("Item code for amount 0:",demo['items'][i]['items'][j]['sku']) 
#         count+=1
# print(count)

























