import json
import allure
import pytest
import requests

from data.data import EMAIL_IS_ALREADY_USED, NOT_ENOUGH_DATA_FOR_CREATION
from global_params import HEADERS, REGISTER_URL
from utils.helpers import generate_new_user_data


@allure.suite("POST /api/auth/register")
@pytest.mark.usefixtures("cleanup_users")
class TestUserCreation:

    # Список созданных пользователей используется для их удаления после выполнения тестов
    CREATED_USERS = []

    @allure.title('Успешное создание уникального пользователя')
    @allure.description(f'Проверяется: в теле ответа имеются данные пользователя и статус код == 200')
    def test_create_unique_user(self):
        with allure.step("Генерация данных для создания пользователя"):
            payload = generate_new_user_data()
            payload_string = json.dumps(payload)

        with allure.step("Отправка POST запроса для создания пользователя"):
            r = requests.post(REGISTER_URL, data=payload_string, headers=HEADERS)

        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(r.json())

        with allure.step(f"Проверка: в теле ответа success == true"):
            assert r.json()["success"] is True
        with allure.step(f"Проверка: в теле ответа есть почта созданного пользователя"):
            assert r.json()["user"]["email"] == payload["email"]
        with allure.step(f"Проверка: в теле ответа есть имя созданного пользователя"):
            assert r.json()["user"]["name"] == payload["name"]
        with allure.step(f"Проверка: в теле ответа есть accessToken"):
            assert len(r.json()["accessToken"]) > 0
        with allure.step(f"Проверка: в теле ответа есть refreshToken"):
            assert len(r.json()["refreshToken"]) > 0
        with allure.step(f"Проверка: статус код == 200"):
            assert r.status_code == 200

    @allure.title('Невозможно создать пользователя, который уже зарегистрирован')
    @allure.description(f'При выполнении теста один и тот же пользователь создается дважды. '
                        f'Проверяется: ошибка == "{EMAIL_IS_ALREADY_USED}" и статус код == 403')
    def test_create_user_only_unique_user_created(self):
        with allure.step("Генерация данных для создания пользователя"):
            payload = generate_new_user_data()
            payload_string = json.dumps(payload)

        with allure.step("Отправка POST запроса для создания пользователя"):
            r_unique = requests.post(REGISTER_URL, data=payload_string, headers=HEADERS)
        with allure.step("Запись пользователя для очистки"):
            self.CREATED_USERS.append(r_unique.json())
        with allure.step("Отправка POST запроса для повторного создания того же пользователя"):
            r_duplicated = requests.post(REGISTER_URL, data=payload_string, headers=HEADERS)

        with allure.step(f"Проверка: ошибка == '{EMAIL_IS_ALREADY_USED}' при повторном создании"):
            assert r_duplicated.json()["message"] == EMAIL_IS_ALREADY_USED
        with allure.step(f"Проверка: код ответа == 403 при повторном создании"):
            assert r_duplicated.status_code == 403

    @pytest.mark.parametrize(
        'missing_field',
        [
            'email',
            'password',
            'name'
        ]
    )
    @allure.title(f'Невозможно создать пользователя без указания обязательного поля')
    @allure.description(f'Проверяется: в теле ошибка == "{NOT_ENOUGH_DATA_FOR_CREATION}" и статус код == 403')
    def test_create_user_user_without_required_field_is_not_created(self, missing_field):
        with allure.step("Генерация данных для создания пользователя"):
            payload = generate_new_user_data([missing_field])
            payload_string = json.dumps(payload)

        with allure.step(f"Отправка POST запроса для создания пользователя без указания параметра {missing_field}"):
            r = requests.post(REGISTER_URL, data=payload_string, headers=HEADERS)

        with allure.step("Запись пользователя для очистки, если запрос был успешен"):
            if r.status_code == 200:
                self.CREATED_USERS.append(r)

        with allure.step(f"Проверка: в теле ошибка == '{NOT_ENOUGH_DATA_FOR_CREATION}'"):
            assert r.json()["message"] == NOT_ENOUGH_DATA_FOR_CREATION
        with allure.step(f"Проверка: код ответа == 403"):
            assert r.status_code == 403
