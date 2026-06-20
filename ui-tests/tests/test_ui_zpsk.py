import allure
import pytest
import re
from playwright.sync_api import expect
from uuid import uuid4

from utils.settings import BASE_URL, CODE, PHONE


def expect_chat_area_visible(page):
    expect(page.get_by_role("button", name="Открыть информацию о чате")).to_be_visible()
    expect(page.get_by_role("button", name="Поиск по чату")).to_be_visible()
    expect(page.get_by_role("button", name="Аудиозвонок")).to_be_visible()
    expect(page.get_by_label("Поиск по сообщениям чата")).to_be_visible()
    expect(page.get_by_placeholder("Сообщение")).to_be_visible()
    expect(page.get_by_role("button", name="Добавить файл")).to_be_visible()
    expect(page.get_by_role("button", name="Отправить")).to_be_visible()


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Авторизация")
@allure.story("Открытие формы входа")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Открытие страницы авторизации")
@allure.description("""
Цель: проверить, что страница авторизации Zapaska WebMessenger открывается и доступна пользователю.

Шаги:
1. Открыть страницу приложения.
2. Проверить заголовок вкладки браузера.
3. Проверить отображение поля номера телефона и кнопки продолжения.

Ожидаемый результат: форма авторизации отображается корректно.
""")
def test_domain(page):
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
@allure.description("""
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
""")
def test_fill_login_form(desktop_page):
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
@allure.description("""
Цель: проверить, что авторизованный пользователь может выйти из аккаунта.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Открыть раздел настроек.
2. Нажать кнопку выхода.
3. Проверить, что открылась форма авторизации.

Ожидаемый результат: пользователь разлогинен, отображаются поле номера телефона и кнопка продолжения.
""")
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
@allure.description("""
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
""")
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
    

@pytest.mark.regression
@allure.parent_suite("UI Zapaska")
@allure.suite("Чаты")
@allure.story("Открытие чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Открытие direct-чата и проверка области сообщений")
@allure.description("""
Цель: проверить, что авторизованный пользователь может открыть direct-чат и увидеть область сообщений.

Предусловия:
- пользователь авторизован через API/cookies;
- direct-чат и уникальное тестовое сообщение созданы через API fixture.

Шаги:
1. Найти созданный direct-чат в списке чатов по уникальному тексту сообщения.
2. Открыть чат.
3. Проверить шапку чата, поиск по сообщениям и область ввода сообщения.

Ожидаемый результат: чат открыт, доступны элементы области сообщений и основные действия в чате.
""")
def test_chat_open(created_direct_chat_with_message, authorized_desktop_page):
    page = authorized_desktop_page
    message_text = created_direct_chat_with_message["search_message_text"]

    with allure.step("Открыть созданный direct-чат"):
        chat_item = page.locator("button.chat-item").filter(has_text=message_text)
        expect(chat_item).to_have_count(1)
        expect(chat_item).to_be_visible()
        chat_item.click()

    with allure.step("Проверить область сообщений и действия в чате"):
        expect_chat_area_visible(page)


@pytest.mark.regression
@allure.parent_suite("UI Zapaska")
@allure.suite("Чаты")
@allure.story("Открытие формы создания чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Открытие формы создания direct-чата")
@allure.description("""
Цель: проверить, что пользователь может открыть форму создания личного чата.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Открыть раздел чатов.
2. Нажать кнопку создания чата.
3. Выбрать тип "Личный чат".
4. Проверить элементы формы выбора участника.

Ожидаемый результат: форма создания direct-чата открыта, отображается заголовок выбора участника и кнопка закрытия формы.
""")
def test_chat_create_form_open(authorized_desktop_page):
    page = authorized_desktop_page

    with allure.step("Открыть форму создания direct-чата"):
        page.get_by_role("button", name="Чаты").click()
        page.get_by_role("button", name="Создать чат").click()
        page.get_by_role("button", name="Личный чат").click()

        expect(page.get_by_text("Выберите участника")).to_be_visible()
        expect(page.get_by_role("button", name="Закрыть создание чата")).to_be_visible()


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Чаты")
@allure.story("Отправка сообщения")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Отправка текстового сообщения")
@allure.description("""
Цель: проверить, что авторизованный пользователь может отправить текстовое сообщение в direct-чат.

Предусловия:
- пользователь авторизован через API/cookies;
- direct-чат и подготовительное сообщение созданы через API fixture.

Шаги:
1. Открыть подготовленный direct-чат по уникальному тексту сообщения.
2. Ввести новое уникальное сообщение в поле ввода.
3. Отправить сообщение.
4. Проверить очистку поля ввода и отображение отправленного сообщения.

Ожидаемый результат: сообщение отправлено, поле ввода очищено, текст сообщения отображается в области сообщений.
""")
def test_send_message(created_direct_chat_with_message, authorized_desktop_page):
    page = authorized_desktop_page
    seed_message_text = created_direct_chat_with_message["search_message_text"]
    message_text = f"AUTOTEST_{uuid4().hex}"
    
    with allure.step("Открыть созданный direct-чат"):
        chat_item = page.locator("button.chat-item").filter(has_text=seed_message_text)
        expect(chat_item).to_have_count(1)
        chat_item.click()

    with allure.step("Отправить сообщение в чат"):
        message_input = page.get_by_placeholder("Сообщение")
        message_input.fill(message_text)
        page.get_by_role("button", name="Отправить").click()

        expect(message_input).to_have_value("")
        expect(page.locator("div.message-content").filter(has_text=message_text)).to_be_visible()
        

    with allure.step("Проверить область сообщений и действия в чате"):
        expect_chat_area_visible(page)


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Поиск")
@allure.story("Поиск чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Поиск чата по имени собеседника")
@allure.description("""
Цель: проверить, что глобальный поиск находит direct-чат по имени собеседника.

Предусловия:
- пользователь авторизован через API/cookies;
- direct-чат с тестовым собеседником создан через API fixture.

Шаги:
1. Ввести имя собеседника в глобальный поиск.
2. Проверить, что найден один подходящий чат.
3. Открыть найденный чат.
4. Проверить имя собеседника в шапке чата.

Ожидаемый результат: поиск возвращает нужный direct-чат, после открытия отображается шапка этого чата.
""")
def test_global_search_by_name(created_direct_chat_with_message, authorized_desktop_page):
    page = authorized_desktop_page
    chat_name = created_direct_chat_with_message["members"][0]["name"]

    with allure.step("Поиск созданного чата"):
        search_input = page.get_by_role("textbox", name="Поиск", exact=True)
        search_input.fill(chat_name)
        found_chat = page.get_by_role(
            "button",
            name=re.compile(rf"^{re.escape(chat_name)}"),
        )

        expect(found_chat).to_have_count(1)
        expect(found_chat).to_contain_text(chat_name)
        
    with allure.step("Открыть найденный чат"):
        found_chat.click()
        expect(page.locator("div.chat-header-text")).to_contain_text(chat_name)


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Поиск")
@allure.story("Поиск чата по сообщению")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Поиск чата по сообщению")
@allure.description("""
Цель: проверить, что глобальный поиск находит direct-чат по тексту сообщения.

Предусловия:
- пользователь авторизован через API/cookies;
- direct-чат и уникальное сообщение созданы через API fixture.

Шаги:
1. Дождаться появления подготовленного сообщения в списке чатов.
2. Ввести текст сообщения в глобальный поиск.
3. Проверить, что в результатах поиска по сообщениям найден один нужный чат.
4. Открыть найденный чат и проверить сообщение в области сообщений.

Ожидаемый результат: поиск возвращает чат с подготовленным сообщением, сообщение отображается после открытия чата.
""")
def test_global_search_by_message(created_direct_chat_with_message, authorized_desktop_page):
    page = authorized_desktop_page
    message_text = created_direct_chat_with_message["search_message_text"]

    with allure.step("Найти чат по тексту сообщения через глобальный поиск"):
        chat_item = page.locator("button.chat-item").filter(has_text=message_text)
        expect(chat_item).to_have_count(1)

        search_input = page.get_by_role("textbox", name="Поиск", exact=True)
        search_input.fill(message_text)

        message_results = page.locator("aside.sidebar div.chat-list").filter(
            has_text="ПО СООБЩЕНИЯМ"
        )
        found_chat = message_results.locator("button.chat-item").filter(
            has_text=message_text
        )

        expect(found_chat).to_have_count(1)
        expect(found_chat).to_contain_text(message_text)

    with allure.step("Открыть найденный чат"):
        found_chat.click()

        expect(
            page.locator("div.message-content").filter(has_text=message_text)
        ).to_be_visible()


@pytest.mark.regression
@allure.parent_suite("UI Zapaska")
@allure.suite("Навигация")
@allure.story("Открытие контакты")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Открытие вкладки 'Контакты'")
@allure.description("""
Цель: проверить, что пользователь может открыть вкладку контактов через основную навигацию.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Найти кнопку "Контакты" в основной навигации.
2. Нажать кнопку "Контакты".
3. Проверить активное состояние вкладки.

Ожидаемый результат: вкладка "Контакты" открыта и отмечена как активная.
""")
def test_contacts_open(authorized_desktop_page):
    page = authorized_desktop_page

    with allure.step("Открыть вкладку Контакты через меню навигации"):
        contacts_tab = page.get_by_role("button", name="Контакты")
        expect(contacts_tab).to_be_visible()
        contacts_tab.click()

    with allure.step("Проверить открытие вкладки Контакты"):
        expect(contacts_tab).to_have_class(re.compile(r".*\bactive\b.*"))
