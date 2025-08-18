import requests

base_url = "http://35.220.164.252:3888/v1/"
api_key = "sk-nD59p1EN85wAVXv9AMQCWbib1LOlJ35aIwun5e7JJ3rSJHlA"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "query": "Hello"
}

try:
    response = requests.post(base_url, headers=headers, json=data, timeout=10)
    print("Status Code:", response.status_code)
    print("Response:", response.text)
except requests.exceptions.RequestException as e:
    print("Request failed:", e)
