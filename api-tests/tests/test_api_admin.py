import allure
import pytest

from config.settings import NAME, PHONE
from models import AdminWhitelistResponse


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Админ")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить Whitelist")
@allure.story("Получить Whitelist")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Получение данных из Whitelist")
@allure.description(
    """
Цель: проверить получение административного whitelist пользователей.

Предусловия:
- пользователь авторизован;
- пользователь имеет права администратора;
- в whitelist есть тестовый пользователь из настроек.

Шаги:
1. Отправить GET-запрос на эндпоинт /auth/admin/whitelist.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать ответ через Pydantic-модель AdminWhitelistResponse.
4. Найти текущего пользователя по номеру телефона.
5. Проверить имя пользователя и уникальность телефонов в whitelist.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ содержит список items;
- текущий пользователь найден в whitelist;
- имя текущего пользователя совпадает с ожидаемым;
- телефоны в whitelist не дублируются.
"""
)
def test_get_admin_whitelist(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные whitelist"):
        response = authorized_api_client.get_whitelist()
        data = attach_api_info(response)

    with allure.step("Проверить данные whitelist"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        whitelist = AdminWhitelistResponse.model_validate(data)
        items = whitelist.items
        assert items

        current_user = next((item for item in items if item.phone == PHONE), None)

        assert (
            current_user is not None
        ), f"Ожидание: пользователь {PHONE} есть в whitelist | Факт: whitelist={data}"
        assert (
            current_user.name == NAME
        ), f"Ожидание: name={NAME!r} | Факт: name={current_user.name!r}"

        phones = [item.phone for item in items]

        assert len(phones) == len(
            set(phones)
        ), f"Ожидание: телефоны в whitelist уникальны | Факт: phones={phones}"
