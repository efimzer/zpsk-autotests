import allure
import pytest

from config.settings import PHONE
from models import ContactItem


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Контакты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить список контактов")
@allure.story("Получить список контактов")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получить список контактов")
@allure.description(
    """
Цель: проверить получение списка контактов текущего пользователя.

Предусловия:
- пользователь авторизован;
- в whitelist есть пользователи, доступные как контакты.

Шаги:
1. Отправить GET-запрос на эндпоинт /contacts.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать элементы ответа через Pydantic-модель ContactItem.
4. Проверить, что текущий пользователь не отображается у себя в контактах.
5. Проверить уникальность телефонов в списке контактов.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ является списком контактов;
- каждый контакт соответствует модели ContactItem;
- телефон текущего пользователя отсутствует в списке;
- телефоны контактов не дублируются.
"""
)
def test_get_contacts(authorized_api_client, attach_api_info):
    with allure.step("Получить список контактов"):
        response = authorized_api_client.get_contacts()
        data = attach_api_info(response)

    with allure.step("Проверить данные списка контактов"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        response_fields = [ContactItem.model_validate(field) for field in data]
        assert response_fields

        phones = [field.phone for field in response_fields]

        assert (
            PHONE not in phones
        ), f"Ожидание: пользователь {PHONE} не должен быть у себя в контактах | Факт: контакты={data}"

        assert len(phones) == len(
            set(phones)
        ), f"Ожидание: телефоны в контактах уникальны | Факт: phones={phones}"
