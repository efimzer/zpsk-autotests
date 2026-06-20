import allure
import pytest

from config.settings import NAME, PHONE
from models import UserProfile


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Профиль")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить данные пользователя")
@allure.story("Текущий пользователь")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение данных авторизованного пользователя")
@allure.description(
    """
Цель: проверить получение профиля текущего авторизованного пользователя.

Предусловия:
- пользователь успешно авторизован;
- cookies авторизованной сессии сохранены в API-клиенте.

Шаги:
1. Отправить GET-запрос на эндпоинт /users/me.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать ответ через Pydantic-модель UserProfile.
4. Проверить телефон и имя пользователя.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ соответствует модели UserProfile;
- phone совпадает с ожидаемым телефоном из тестовых настроек;
- name совпадает с ожидаемым именем из тестовых настроек.
"""
)
def test_get_current_user_profile(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные профиля"):
        response = authorized_api_client.get_user_profile()
        user_profile = attach_api_info(response)

    with allure.step("Проверить данные профиля"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        profile = UserProfile.model_validate(user_profile)

        assert (
            profile.phone == PHONE
        ), f"Ожидание: phone={PHONE!r} | Факт: phone={profile.phone!r}"
        assert (
            profile.name == NAME
        ), f"Ожидание: name={NAME!r} | Факт: name={profile.name!r}"
