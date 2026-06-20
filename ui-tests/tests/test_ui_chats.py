from uuid import uuid4

import allure
import pytest
from playwright.sync_api import expect


def expect_chat_area_visible(page):
    expect(page.get_by_role("button", name="Открыть информацию о чате")).to_be_visible()
    expect(page.get_by_role("button", name="Поиск по чату")).to_be_visible()
    expect(page.get_by_role("button", name="Аудиозвонок")).to_be_visible()
    expect(page.get_by_label("Поиск по сообщениям чата")).to_be_visible()
    expect(page.get_by_placeholder("Сообщение")).to_be_visible()
    expect(page.get_by_role("button", name="Добавить файл")).to_be_visible()
    expect(page.get_by_role("button", name="Отправить")).to_be_visible()


@pytest.mark.regression
@allure.parent_suite("UI Zapaska")
@allure.suite("Чаты")
@allure.story("Открытие чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Открытие direct-чата и проверка области сообщений")
@allure.description(
    """
Цель: проверить, что авторизованный пользователь может открыть direct-чат и увидеть область сообщений.

Предусловия:
- пользователь авторизован через API/cookies;
- direct-чат и уникальное тестовое сообщение созданы через API fixture.

Шаги:
1. Найти созданный direct-чат в списке чатов по уникальному тексту сообщения.
2. Открыть чат.
3. Проверить шапку чата, поиск по сообщениям и область ввода сообщения.

Ожидаемый результат: чат открыт, доступны элементы области сообщений и основные действия в чате.
"""
)
def test_direct_chat_can_be_opened(
    direct_chat_with_seed_message, authorized_desktop_page
):
    page = authorized_desktop_page
    message_text = direct_chat_with_seed_message["message_text"]

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
@allure.description(
    """
Цель: проверить, что пользователь может открыть форму создания личного чата.

Предусловия:
- пользователь авторизован через API/cookies.

Шаги:
1. Открыть раздел чатов.
2. Нажать кнопку создания чата.
3. Выбрать тип "Личный чат".
4. Проверить элементы формы выбора участника.

Ожидаемый результат: форма создания direct-чата открыта, отображается заголовок выбора участника и кнопка закрытия формы.
"""
)
def test_direct_chat_creation_form_can_be_opened(authorized_desktop_page):
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
@allure.description(
    """
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
"""
)
def test_user_can_send_text_message(
    direct_chat_with_seed_message, authorized_desktop_page
):
    page = authorized_desktop_page
    seed_message_text = direct_chat_with_seed_message["message_text"]
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
        expect(
            page.locator("div.message-content").filter(has_text=message_text)
        ).to_be_visible()

    with allure.step("Проверить область сообщений и действия в чате"):
        expect_chat_area_visible(page)
