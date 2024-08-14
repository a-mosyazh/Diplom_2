import json
import allure
import pytest
import requests

from data.data import INGREDIENTS, INGREDIENTS_MUST_BE_PROVIDED, NO_INGREDIENTS, INVALID_INGREDIENTS
from global_params import HEADERS, ORDERS_URL
from utils.helpers import create_user_and_return_login_password, add_auth_to_headers


@allure.suite("POST /api/orders")
@pytest.mark.usefixtures("cleanup_users")
class TestOrderCreation:

    # Список созданных пользователей используется для их удаления после выполнения тестов
    CREATED_USERS = []

    @allure.title(f'Успешное создание заказа для авторизованного пользователя')
    @allure.description(f'Проверяется: в теле имеется owner и статус код == 200')
    def test_create_order_successful_creation_for_authorized_user(self):
        with allure.step("Создание пользователя"):
            created_user = create_user_and_return_login_password()
        with allure.step("Дополнение заголовков авторизацией"):
            headers_payload = add_auth_to_headers(created_user["accessToken"])
            payload_string = json.dumps(INGREDIENTS)

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(created_user)

        with allure.step("Отправка POST запроса для создания заказа"):
            r = requests.post(ORDERS_URL, data=payload_string, headers=headers_payload)

        with allure.step(f"Проверка: в теле ответа owner.email равен почте авторизованного пользователя"):
            assert r.json()['order']['owner']['email'] == created_user['user']['email']
        with allure.step(f"Проверка: в теле ответа в order параметров больше одного"):
            assert len(r.json()['order']) > 1
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title(f'Успешное создание заказа без использования авторизации')
    @allure.description(f'Проверяется: в теле нет owner и статус код == 200')
    def test_create_order_successful_creation_no_auth(self):
        payload_string = json.dumps(INGREDIENTS)
        with allure.step("Отправка POST запроса для создания заказа"):
            r = requests.post(ORDERS_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: в теле ответа нет owner.email"):
            assert r.json()['order'].get('owner') is None
        with allure.step(f"Проверка: в теле ответа в order только один параметр"):
            assert len(r.json()['order']) == 1
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title(f'Заказ не может быть создан без ингредиентов')
    @allure.description(f'Проверяется: в теле message = {INGREDIENTS_MUST_BE_PROVIDED} и статус код == 400')
    def test_create_order_order_is_not_created_without_ingredients(self):
        payload_string = json.dumps(NO_INGREDIENTS)
        with allure.step("Отправка POST запроса для создания заказа"):
            r = requests.post(ORDERS_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: в теле message = {INGREDIENTS_MUST_BE_PROVIDED}"):
            assert r.json()['message'] == INGREDIENTS_MUST_BE_PROVIDED
        with allure.step(f"Проверка: статус код == 400"):
            assert r.status_code == 400

    @allure.title(f'Заказ не может быть создан с неверным хэшем ингредиентов')
    @allure.description(f'Проверяется: статус код == 500')
    def test_create_order_order_is_not_created_with_invalid_hash_of_ingredient(self):
        payload_string = json.dumps(INVALID_INGREDIENTS)
        with allure.step("Отправка POST запроса для создания заказа"):
            r = requests.post(ORDERS_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: статус код == 500"):
            assert r.status_code == 500
