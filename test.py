import requests

# # url = "http://localhost:8000/users/user/1/edit/"

# # data = {
# #     "username": "ali",
# #     "first_name": "3",
# #     "last_name": "4",
# #     "middle_name": "5",
# #     "image": 56
# # }

# # res = requests.post(url, data=data)

# # print(res.text)

# url = "http://147.45.158.162:9060/courses/"
data = {
    "username": "hello",
    "password": "123"
}

# headers = {
#     "Authorization": 'Token f5783617d3524fbabc7d499107b98aa57b7a10f7'
# }

# res = requests.get(url, headers=headers)

url = "http://localhost:8000/users/signup/"

# # data = {
# #     "username": "hello",
# #     "first_name": "Alisher",
# #     "last_name": "Abdimuminov",
# #     "middle_name": "Abdimuminov",
# #     "bio": "Baxodir o'g'li",
# #     "password": "123"
# # }

res = requests.post(url, data)

print(res.text)
