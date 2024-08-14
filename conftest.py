import pytest

from utils.helpers import delete_user


# Фикстура для удаления созданных в ходе тестов пользователей
@pytest.fixture(scope='class')
def cleanup_users(request):
    def delete_users():
        for user in request.cls.CREATED_USERS:
            delete_user(user['accessToken'])

    request.addfinalizer(delete_users)
