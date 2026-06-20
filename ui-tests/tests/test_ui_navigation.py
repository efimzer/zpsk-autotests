import re

import allure
import pytest
from playwright.sync_api import expect


@pytest.mark.regression
@allure.parent_suite("UI Zapaska")
@allure.suite("Навигация")
@allure.story("Открытие контакты")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Открытие вкладки 'Контакты'")
@allure.description(
    """
Цель: проверить, что пользователь может открыть вкладку контактов через основную навигацию.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Найти кнопку "Контакты" в основной навигации.
2. Нажать кнопку "Контакты".
3. Проверить активное состояние вкладки.

Ожидаемый результат: вкладка "Контакты" открыта и отмечена как активная.
"""
)
def test_contacts_tab_becomes_active(authorized_desktop_page):
    page = authorized_desktop_page

    with allure.step("Открыть вкладку Контакты через меню навигации"):
        contacts_tab = page.get_by_role("button", name="Контакты")
        expect(contacts_tab).to_be_visible()
        contacts_tab.click()

    with allure.step("Проверить открытие вкладки Контакты"):
        expect(contacts_tab).to_have_class(re.compile(r".*\bactive\b.*"))
