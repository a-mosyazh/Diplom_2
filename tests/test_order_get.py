import json

import allure
import pytest
import requests

from data.data import INGREDIENTS, SHOULD_BE_AUTHORISED
from global_params import HEADERS, ORDERS_URL
from utils.helpers import create_user_and_return_login_password, add_auth_to_headers


@allure.suite("GET /api/orders")
@pytest.mark.usefixtures("cleanup_users")
class TestOrderGet:

    # Список созданных пользователей используется для их удаления после выполнения тестов
    CREATED_USERS = []

    @allure.title(f'Успешное получение заказов пользователя')
    @allure.description(f'Проверяется: в теле имеется заказ и статус код == 200')
    def test_get_order_successful_for_authorized_user(self):
        with allure.step("Создание пользователя"):
            created_user = create_user_and_return_login_password()
        with allure.step("Дополнение заголовков авторизацией"):
            headers_payload = add_auth_to_headers(created_user["accessToken"])
            payload_string = json.dumps(INGREDIENTS)

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(created_user)

        with allure.step("Отправка POST запроса для создания заказа"):
            order = requests.post(ORDERS_URL, data=payload_string, headers=headers_payload)

        with allure.step("Отправка GET запроса для получения заказа"):
            r = requests.get(ORDERS_URL, headers=headers_payload)

        with allure.step(f"Проверка: в теле ответа order_id при создании и получении заказа совпадает"):
            assert r.json()['orders'][0]['_id'] == order.json()['order']['_id']
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title(f'Невозможно получить список заказов без указания пользователя')
    @allure.description(f'Проверяется: в теле message == {SHOULD_BE_AUTHORISED} и статус код == 401')
    def test_get_order_no_order_list_for_unauthorized_user(self):
        with allure.step("Отправка GET запроса без авторизации для получения заказа"):
            r = requests.get(ORDERS_URL, headers=HEADERS)

        with allure.step(f"Проверка: в теле message == {SHOULD_BE_AUTHORISED}"):
            assert r.json()['message'] == SHOULD_BE_AUTHORISED
        with allure.step(f"Проверка: статус код == 401"):
            assert r.status_code == 401
