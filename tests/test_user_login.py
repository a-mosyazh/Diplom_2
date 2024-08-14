import json
import allure
import pytest
import requests

from data.data import EMAIL_OR_PASSWORD_INCORRECT
from global_params import HEADERS, LOGIN_URL
from utils.helpers import create_user_and_return_login_password, delete_user


@allure.suite("POST /api/auth/login")
@pytest.mark.usefixtures("cleanup_users")
class TestUserLogin:

    # Список созданных пользователей используется для их удаления после выполнения тестов
    CREATED_USERS = []

    @allure.title('Успешный логин пользователя в системе с использованием почты и пароля')
    @allure.description('Проверяется: в теле есть данные пользователя и статус код == 200')
    def test_login_user_login_with_email_and_password(self):
        with allure.step("Регистрация пользователя"):
            payload = create_user_and_return_login_password()["user"]
            payload_string = json.dumps(payload)

        with allure.step("Отправка POST запроса для входа пользователя в систему"):
            r = requests.post(LOGIN_URL, data=payload_string, headers=HEADERS)

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(r.json())

        with allure.step(f"Проверка: в теле ответа success == true"):
            assert r.json()["success"] is True
        with allure.step(f"Проверка: в теле ответа есть почта созданного пользователя"):
            assert r.json()["user"]["email"] == payload["email"]
        with allure.step(f"Проверка: в теле ответа есть имя созданного пользователя"):
            assert len(r.json()["user"]["name"]) > 0
        with allure.step(f"Проверка: в теле ответа есть accessToken"):
            assert len(r.json()["accessToken"]) > 0
        with allure.step(f"Проверка: в теле ответа есть refreshToken"):
            assert len(r.json()["refreshToken"]) > 0
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title('Невозможно войти в систему, используя даные несуществующего пользователя')
    @allure.description(f'Для проверки создается и удаляется пользователь, под которым затем происходит попытка входа.'
                        f'Проверяется: в теле ошибка == "{EMAIL_OR_PASSWORD_INCORRECT}" и статус код == 401')
    def test_login_user_non_existent_user_cannot_login(self):
        with allure.step("Создание пользователя"):
            payload = create_user_and_return_login_password()
            payload_string = json.dumps(payload["user"])

        with allure.step("Удаление пользователя"):
            delete_user(payload["accessToken"])

        with allure.step("Отправка POST запроса для входа пользователя в систему"):
            r = requests.post(LOGIN_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: в теле ошибка == '{EMAIL_OR_PASSWORD_INCORRECT}'"):
            assert r.json()['message'] == EMAIL_OR_PASSWORD_INCORRECT
        with allure.step(f"Проверка: статус код == 401"):
            assert r.status_code == 401
