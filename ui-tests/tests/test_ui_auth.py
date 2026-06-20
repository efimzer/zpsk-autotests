import allure
import pytest
from playwright.sync_api import expect

from utils.settings import BASE_URL, CODE, PHONE


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Авторизация")
@allure.story("Открытие формы входа")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Открытие страницы авторизации")
@allure.description(
    """
Цель: проверить, что страница авторизации Zapaska WebMessenger открывается и доступна пользователю.

Шаги:
1. Открыть страницу приложения.
2. Проверить заголовок вкладки браузера.
3. Проверить отображение поля номера телефона и кнопки продолжения.

Ожидаемый результат: форма авторизации отображается корректно.
"""
)
def test_authorization_page_is_opened(page):
    with allure.step("Открыть страницу приложения"):
        page.goto(BASE_URL)

    with allure.step("Проверить, что форма авторизации отображается"):
        expect(page).to_have_title("Zapaska WebMessenger")
        expect(page.get_by_label("Номер телефона")).to_be_visible()
        expect(page.get_by_role("button", name="Продолжить")).to_be_visible()


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Авторизация")
@allure.story("Вход по коду")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Успешный вход через UI-форму")
@allure.description(
    """
Цель: проверить успешную авторизацию пользователя через UI-форму по номеру телефона и коду подтверждения.

Предусловия:
- тестовый пользователь существует;
- код подтверждения валиден для тестового пользователя.

Шаги:
1. Открыть страницу приложения.
2. Ввести номер телефона.
3. Ввести код подтверждения.
4. Проверить, что открылась основная страница мессенджера.

Ожидаемый результат: форма авторизации скрыта, отображается основная навигация приложения.
"""
)
def test_user_can_login_with_valid_code(desktop_page):
    page = desktop_page

    with allure.step("Открыть страницу приложения"):
        page.goto(BASE_URL)

    with allure.step("Ввести номер телефона и перейти к вводу кода"):
        page.get_by_label("Номер телефона").fill(PHONE)
        page.get_by_role("button", name="Продолжить").click()

    with allure.step("Ввести код подтверждения"):
        for i, digit in enumerate(CODE, start=1):
            page.get_by_label(f"Цифра {i}").fill(digit)

    with allure.step("Проверить, что открылась основная страница"):
        expect(page.get_by_label("Номер телефона")).not_to_be_visible()
        expect(page.get_by_role("navigation", name="Навигация")).to_be_visible()
        expect(page.get_by_role("button", name="Контакты")).to_be_visible()
        expect(page.get_by_role("button", name="Звонки")).to_be_visible()
        expect(page.get_by_role("button", name="Чаты")).to_be_visible()
        expect(page.get_by_role("button", name="Настройки")).to_be_visible()
        expect(page.get_by_role("button", name="Создать чат")).to_be_visible()


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Авторизация")
@allure.story("Выход из аккаунта")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Выход из аккаунта")
@allure.description(
    """
Цель: проверить, что авторизованный пользователь может выйти из аккаунта.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Открыть раздел настроек.
2. Нажать кнопку выхода.
3. Проверить, что открылась форма авторизации.

Ожидаемый результат: пользователь разлогинен, отображаются поле номера телефона и кнопка продолжения.
"""
)
def test_logout(authorized_desktop_page):
    page = authorized_desktop_page

    with allure.step("Перейти на страницу Настройки"):
        page.get_by_role("button", name="Настройки").click()

        expect(page.locator("header.settings-sidebar-header")).to_have_text("Настройки")

    with allure.step("Нажать Logout"):
        page.get_by_role("button", name="Выйти").click()

    with allure.step("Проверить, что отображается страница Login"):
        expect(page.get_by_label("Номер телефона")).to_be_visible()
        expect(page.get_by_role("button", name="Продолжить")).to_be_visible()


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Авторизация")
@allure.story("Вход с неверным кодом")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Попытка входа с неверным кодом")
@allure.description(
    """
Цель: проверить, что пользователь не может войти в приложение с неверным кодом подтверждения.

Предусловия:
- тестовый пользователь существует;
- введенный код подтверждения невалиден.

Шаги:
1. Открыть страницу приложения.
2. Ввести номер телефона.
3. Ввести неверный код подтверждения.
4. Проверить текст ошибки и отсутствие основной навигации.

Ожидаемый результат: вход не выполнен, отображается ошибка "Неверный код".
"""
)
def test_login_with_invalid_code(desktop_page):
    page = desktop_page

    with allure.step("Открыть страницу приложения"):
        page.goto(BASE_URL)

    with allure.step("Ввести номер телефона и перейти к вводу кода"):
        page.get_by_label("Номер телефона").fill(PHONE)
        page.get_by_role("button", name="Продолжить").click()

    with allure.step("Ввести неверный код подтверждения"):
        for i, digit in enumerate("0000", start=1):
            page.get_by_label(f"Цифра {i}").fill(digit)

    with allure.step("Проверить, что отображается ошибка 'Неверный код'"):
        expect(page.get_by_role("status")).to_have_text("Неверный код")
        expect(page.get_by_role("navigation", name="Навигация")).not_to_be_visible()
        expect(page.get_by_role("button", name="Сбросить код-пароль")).to_be_visible()
