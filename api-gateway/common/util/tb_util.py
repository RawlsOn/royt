# BASE_URL = 'http://thingsboard:9090'
# DEVICE_TOKEN = '3pGhzfU2OLPdhsjF4rCg'

# import requests

# def send(telemetry):
#     url = BASE_URL + '/api/v1/' + DEVICE_TOKEN + '/telemetry'
#     headers = {
#         'Content-Type': 'application/json',
#         'Accept': 'application/json'
#     }
#     response = requests.post(url, headers=headers, json=telemetry)
#     print(response.status_code)
#     print(response.text)