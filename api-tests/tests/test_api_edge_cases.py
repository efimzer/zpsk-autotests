import allure
import pytest

from config.settings import PHONE


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Негативные сценарии")
@allure.feature("Авторизация")
@allure.story("Негативная авторизация")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Отказ в авторизации с невалидным кодом")
@allure.description(
    """
Цель: проверить, что система не авторизует пользователя при вводе неверного кода подтверждения или кода в невалидном формате.

Предусловия:
- номер телефона существует на stage-окружении;
- передаваемый код подтверждения неверный или не соответствует формату из 4 цифр.

Шаги:
1. Отправить POST-запрос на эндпоинт /auth/login.
2. Передать существующий номер телефона и невалидный код подтверждения.
3. Получить и разобрать JSON-ответ сервера.

Ожидаемый результат:
- сервер возвращает HTTP 401 для неверного цифрового кода;
- сервер возвращает HTTP 400 для кода в неверном формате;
- авторизованная сессия не создается;
- в ответе приходит ожидаемое сообщение об ошибке.
"""
)
@pytest.mark.parametrize(
    "invalid_code, expected_status, expected_message",
    [
        pytest.param("0000", 401, "Неверный код", id="digits"),
        pytest.param("abcd", 400, "Код должен содержать 4 цифры", id="latin"),
        pytest.param("тест", 400, "Код должен содержать 4 цифры", id="cyrillic"),
        pytest.param("!@#$", 400, "Код должен содержать 4 цифры", id="special"),
        pytest.param("🙂🙃", 400, "Код должен содержать 4 цифры", id="emoji"),
    ],
)
def test_login_with_invalid_code(
    api_client,
    attach_api_info,
    invalid_code,
    expected_status,
    expected_message,
):
    with allure.step("Отправить запрос авторизации с неверным кодом"):
        response = api_client.login(PHONE, invalid_code)

        data = attach_api_info(response, request_body={"phone": PHONE, "code": "****"})

    with allure.step("Проверить отказ в авторизации"):
        assert (
            response.status_code == expected_status
        ), f"Ожидание: HTTP {expected_status} | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert (
            data["message"] == expected_message
        ), f"Ожидание: message={expected_message!r} | Факт: message={data.get('message')!r}, тело ответа={data}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Негативные сценарии")
@allure.feature("Авторизация")
@allure.story("Доступ без авторизации")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Получение /auth/me без авторизации")
@allure.description(
    """
Цель: проверить корректное поведение эндпоинта /auth/me для неавторизованного пользователя.

Предусловия:
- запрос выполняется через неавторизованный API-клиент;
- cookies авторизованной сессии отсутствуют.

Шаги:
1. Отправить GET-запрос на эндпоинт /auth/me без авторизации.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить признак авторизации пользователя.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- запрос обрабатывается без ошибки;
- в ответе приходит authenticated=False.
"""
)
def test_get_auth_me_without_authorization(api_client, attach_api_info):
    with allure.step("Запросить /auth/me без авторизационных cookies"):
        response = api_client.get_auth_me()

        auth_me = attach_api_info(response)

    with allure.step("Проверить состояние неавторизованного пользователя"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert (
            auth_me["authenticated"] is False
        ), f"Ожидание: authenticated=False | Факт: тело ответа={auth_me}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Негативные сценарии")
@allure.feature("Чаты")
@allure.story("Доступ без авторизации")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Запрет получения списка чатов без авторизации")
@allure.description(
    """
Цель: проверить, что неавторизованный пользователь не может получить список чатов.

Предусловия:
- запрос выполняется через неавторизованный API-клиент;
- cookies авторизованной сессии отсутствуют.

Шаги:
1. Отправить GET-запрос на эндпоинт /chats без авторизации.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить статус ответа и текст ошибки.

Ожидаемый результат:
- сервер возвращает HTTP 401;
- список чатов не возвращается как доступный ресурс;
- в ответе приходит сообщение "Требуется авторизация".
"""
)
def test_get_chats_without_authorization(api_client, attach_api_info):
    with allure.step("Запросить список чатов без авторизационных cookies"):
        response = api_client.get_chats()

        data = attach_api_info(response)

    with allure.step("Проверить запрет доступа к списку чатов"):
        assert (
            response.status_code == 401
        ), f"Ожидание: HTTP 401 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert (
            data["message"] == "Требуется авторизация"
        ), f"Ожидание: message='Требуется авторизация' | Факт: message={data.get('message')!r}, тело ответа={data}"
