import allure
import pytest

from config.settings import CODE, NAME, PHONE
from helpers.assertions import assert_uuid


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Авторизация")
@allure.story("Вход по коду")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Успешная авторизация по коду")
@allure.description(
    """
Цель: проверить, что пользователь может успешно авторизоваться по номеру телефона и коду подтверждения.

Предусловия:
- номер телефона существует на stage-окружении;
- код подтверждения валиден для указанного номера.

Шаги:
1. Отправить POST-запрос на эндпоинт /auth/login.
2. Передать в теле запроса номер телефона и код подтверждения.
3. Получить и разобрать JSON-ответ сервера.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- в ответе приходит ok=True;
- имя пользователя соответствует ожидаемому значению из тестовых настроек.
"""
)
def test_login_with_valid_code(api_client, attach_api_info):
    with allure.step("Отправить запрос авторизации с валидным кодом"):
        response = api_client.login(PHONE, CODE)

        data = attach_api_info(response, request_body={"phone": PHONE, "code": "****"})

    with allure.step("Проверить успешную авторизацию пользователя"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert data["ok"] is True, f"Ожидание: ok=True | Факт: тело ответа={data}"
        assert (
            data["name"] == NAME
        ), f"Ожидание: name={NAME!r} | Факт: name={data['name']!r}"


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Авторизация")
@allure.story("Текущий пользователь")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение текущего авторизованного пользователя")
@allure.description(
    """
Цель: проверить, что авторизованная сессия возвращает данные текущего пользователя.

Предусловия:
- пользователь успешно авторизован через фикстуру authorized_api_client;
- cookies авторизованной сессии сохранены в API-клиенте.

Шаги:
1. Отправить GET-запрос на эндпоинт /auth/me.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить признаки авторизованной сессии и данные пользователя.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- authenticated=True;
- id пользователя имеет формат UUID;
- номер телефона совпадает с ожидаемым номером из тестовых настроек.
"""
)
def test_get_current_user(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные текущего пользователя"):
        response = authorized_api_client.get_auth_me()

        auth_me = attach_api_info(response)

    with allure.step("Проверить данные текущего пользователя"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert (
            auth_me["authenticated"] is True
        ), f"Ожидание: authenticated=True | Факт: тело ответа={auth_me}"
        assert_uuid(auth_me["id"], "auth_me.id")
        assert (
            auth_me["phone"] == PHONE
        ), f"Ожидание: phone={PHONE!r} | Факт: phone={auth_me['phone']!r}"
