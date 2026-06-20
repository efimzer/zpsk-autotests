import re

import allure
import pytest
from playwright.sync_api import expect


def find_chat_by_message_search(page, message_text):
    search_input = page.get_by_role("textbox", name="Поиск", exact=True)
    message_results = page.locator("aside.sidebar div.chat-list").filter(
        has_text="ПО СООБЩЕНИЯМ"
    )
    found_chat = message_results.locator("button.chat-item")
    last_error = None

    for _ in range(4):
        search_input.fill("")
        search_input.fill(message_text)

        try:
            expect(found_chat).to_have_count(1, timeout=5000)
            expect(found_chat).to_contain_text(message_text)
            return found_chat
        except AssertionError as error:
            last_error = error
            page.wait_for_timeout(2000)

    raise last_error


@pytest.mark.smoke
@allure.parent_suite("UI Zapaska")
@allure.suite("Поиск")
@allure.story("Поиск чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Поиск чата по имени собеседника")
@allure.description(
    """
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
"""
)
def test_global_search_finds_chat_by_name(
    direct_chat_with_seed_message, authorized_desktop_page
):
    page = authorized_desktop_page
    chat_name = direct_chat_with_seed_message["chat"]["members"][0]["name"]

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
@allure.description(
    """
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
"""
)
def test_global_search_finds_chat_by_message(
    direct_chat_with_seed_message, authorized_desktop_page
):
    page = authorized_desktop_page
    message_text = direct_chat_with_seed_message["message_text"]

    with allure.step("Найти чат по тексту сообщения через глобальный поиск"):
        chat_item = page.locator("button.chat-item").filter(has_text=message_text)
        expect(chat_item).to_have_count(1)

        found_chat = find_chat_by_message_search(page, message_text)

    with allure.step("Открыть найденный чат"):
        found_chat.click()

        expect(
            page.locator("div.message-content").filter(has_text=message_text)
        ).to_be_visible()
