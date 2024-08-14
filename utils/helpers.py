import datetime
import json

import requests
from faker import Faker

from global_params import HEADERS, USER_URL, REGISTER_URL

fake = Faker()


def generate_new_user_data(exclude_parameter=None):
    if exclude_parameter is None:
        exclude_parameter = []

    now = datetime.datetime.now()
    timestamp = datetime.datetime.timestamp(now)
    unique_part = str(timestamp).replace('.', '')

    email = f'{unique_part}_{fake.email(domain='yandex.ru')}'
    password = fake.password(15)
    name = fake.name()

    payload = {
        "email": email,
        "password": password,
        "name": name
    }

    if len(exclude_parameter) > 0:
        for i in exclude_parameter:
            del payload[i]

    return payload


def create_user_and_return_login_password():
    payload = generate_new_user_data()
    payload_string = json.dumps(payload)
    response = requests.post(REGISTER_URL, data=payload_string, headers=HEADERS)

    if response.status_code == 200:
        payload = {
            "user": {
                "email": payload["email"],
                "password": payload["password"]
            },
            "accessToken": response.json()["accessToken"]
        }
        return payload


def add_auth_to_headers(token):
    headers_payload = HEADERS.copy()
    headers_payload["Authorization"] = str(token)
    return headers_payload


def delete_user(token):
    headers_payload = add_auth_to_headers(token)
    requests.delete(USER_URL, headers=headers_payload)
