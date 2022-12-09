import json

import requests
import pprint

HOST = 'http://127.0.0.1:5000'

# def post():
#     post_data = {
#         'id': 1,
#         'title': 'Selling an aquarium fish',
#         'description': 'Guppi fish, really cute',
#         'owner': 'Mike'
#     }
#     response = requests.post(f'{HOST}/advertisements/', json=post_data)

data = requests.post('http://127.0.0.1:5000/advert/',
                     json={
                         'id': 1,
                         'title': 'Selling an aquarium fish',
                         'description': 'Guppi fish, really cute',
                         'owner': 'Mike'})
print(data.status_code)
print(data.text)

# def get():
#     response = requests.get(f'{HOST}/advertisements/1')
#     print(response.json())
#
#
# def delete():
#     response = requests.delete(f'{HOST}/advertisements/1')
#     print(response.json())
