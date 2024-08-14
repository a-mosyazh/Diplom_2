import json
import allure
import pytest
import requests

from data.data import SHOULD_BE_AUTHORISED
from global_params import HEADERS, USER_URL
from utils.helpers import create_user_and_return_login_password, generate_new_user_data, add_auth_to_headers


@allure.suite("PATCH /api/auth/user")
@pytest.mark.usefixtures("cleanup_users")
class TestUserUpdate:

    # Список созданных пользователей используется для их удаления после выполнения тестов
    CREATED_USERS = []

    @allure.title(f'Успешное обновление имени и почты пользователя')
    @allure.description(f'Проверяется: в теле ответа есть обновленные параметры и статус код == 200')
    def test_update_user_successfully(self):
        with allure.step("Создание пользователя"):
            created_user = create_user_and_return_login_password()

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(created_user)

        with allure.step("Генерация новых значений для пользователя"):
            payload = generate_new_user_data(["password"])
            payload_string = json.dumps(payload)

        with allure.step("Дополнение заголовков авторизацией"):
            headers_payload = add_auth_to_headers(created_user["accessToken"])

        with allure.step("Отправка PATCH запроса для обновления пользователя"):
            r = requests.patch(USER_URL, data=payload_string, headers=headers_payload)

        with allure.step(f"Проверка: в теле ответа success == true"):
            assert r.json()["success"] is True
        with allure.step(f"Проверка: в теле ответа есть почта созданного пользователя"):
            assert r.json()["user"]["email"] == payload["email"]
        with allure.step(f"Проверка: в теле ответа есть имя созданного пользователя"):
            assert r.json()["user"]["name"] == payload["name"]
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title('Невозможно обновить данные пользователя, не используя авторизацию')
    @allure.description(f'Проверяется: в теле ошибка == "{SHOULD_BE_AUTHORISED}" и статус код == 401.')
    def test_update_user_cannot_update_without_auth(self):
        with allure.step("Создание пользователя"):
            created_user = create_user_and_return_login_password()

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(created_user)

        with allure.step("Получение новых значений для пользователя"):
            payload = generate_new_user_data(["password"])
            payload_string = json.dumps(payload)

        with allure.step("Отправка PATCH запроса для обновления пользователя без токена в заголовках"):
            r = requests.patch(USER_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: в теле ответа message == '{SHOULD_BE_AUTHORISED}'"):
            assert r.json()["message"] == SHOULD_BE_AUTHORISED
        with allure.step(f"Проверка: статус код == 401"):
            assert r.status_code == 401
