## Дипломный проект. Задание 2: API

### Автотесты для проверки ручек https://stellarburgers.nomoreparties.site/api, которые помогают заказать бургер в Stellar Burgers

### Реализованные сценарии

Созданы API тесты, покрывающие ручки `/api/orders`, `/api/orders`, `/api/auth/register`, `/api/auth/login`, `/api/auth/user`

Результаты тестирования собраны в allure-отчет

### Структура проекта

- `tests` - пакет, содержащий тесты, разделенные по ручкам. Например, `test_order_create.py`, `test_user_update.py` и т.д.
- `allure_results` - пакет, содержащий allure-отчет
- `data` - пакет, содержищий данные, использующиеся в тестах
- `utils` - пакет, содержащий вспомогательные команды

### Запуск автотестов

Перед запуском тестов убедитесь, что у вас установлен Python версии 3 и выше

**Установка зависимостей**

> `$ pip install -r requirements.txt`

**Запуск автотестов и создание allure-отчета с результатами**

>  `$ pytest tests/ --alluredir=allure_results`

**Просмотр allure-отчета с результатами**

>  `$ allure serve allure_results`
