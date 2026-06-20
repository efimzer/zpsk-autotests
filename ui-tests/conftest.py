from uuid import uuid4
from pathlib import Path

import allure
import pytest
from playwright.sync_api import Error as PlaywrightError, expect

from api.api_client import ApiClient
from utils.settings import BASE_URL, CODE, PHONE, PHONE_PARTICIPANT


ATTACHMENT_TYPES = {
    ".png": allure.attachment_type.PNG,
    ".zip": allure.attachment_type.ZIP,
    ".webm": allure.attachment_type.WEBM,
}


def get_test_page(item):
    for fixture_name in ("authorized_desktop_page", "desktop_page", "page"):
        candidate = item.funcargs.get(fixture_name)
        if candidate and not candidate.is_closed():
            return candidate
    return None


def attach_failure_screenshot(item):
    page = get_test_page(item)
    if not page:
        return

    try:
        screenshot = page.screenshot(timeout=3000)
        allure.attach(
            screenshot,
            name="Screenshot on failure",
            attachment_type=allure.attachment_type.PNG,
        )
        item._failure_screenshot_attached = True
    except PlaywrightError as error:
        allure.attach(
            str(error),
            name="Screenshot was not captured",
            attachment_type=allure.attachment_type.TEXT,
        )


def attach_playwright_artifacts(item):
    output_path = item.funcargs.get("output_path")
    if not output_path:
        return

    artifacts_dir = Path(output_path)
    if not artifacts_dir.exists():
        return

    for artifact in sorted(path for path in artifacts_dir.rglob("*") if path.is_file()):
        attachment_type = ATTACHMENT_TYPES.get(artifact.suffix.lower())
        if not attachment_type:
            continue
        allure.attach.file(
            str(artifact),
            name=f"Playwright {artifact.name}",
            attachment_type=attachment_type,
        )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)

    if report.when == "call" and report.failed:
        attach_failure_screenshot(item)

    if report.when == "teardown":
        setup_report = getattr(item, "rep_setup", None)
        call_report = getattr(item, "rep_call", None)
        failed = (setup_report and setup_report.failed) or (
            call_report and call_report.failed
        )
        if failed:
            attach_playwright_artifacts(item)


@pytest.fixture
def desktop_page(page):
    page.set_viewport_size({"width": 1440, "height": 900})
    return page


@pytest.fixture
def api_client():
    return ApiClient(BASE_URL)


@pytest.fixture
def authorized_api_client(api_client):
    with allure.step("API: авторизоваться тестовым пользователем"):
        response = api_client.login(PHONE, CODE)

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при API-авторизации | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    return api_client


def add_api_cookies_to_context(context, api_client):
    cookies = []

    with allure.step("Перенести cookies API-сессии в браузер"):
        for cookie in api_client.session.cookies:
            same_site = cookie._rest.get("SameSite", "Lax")
            if same_site not in {"Strict", "Lax", "None"}:
                same_site = "Lax"

            playwright_cookie = {
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path or "/",
                "httpOnly": "HttpOnly" in cookie._rest,
                "secure": cookie.secure,
                "sameSite": same_site,
            }

            if cookie.expires is not None:
                playwright_cookie["expires"] = cookie.expires

            cookies.append(playwright_cookie)

        assert cookies, "API-логин не вернул cookies"
        context.add_cookies(cookies)


@pytest.fixture
def created_direct_chat(authorized_api_client):
    assert PHONE_PARTICIPANT, "Не задана переменная окружения PHONE_PARTICIPANT"

    with allure.step("API: создать direct-чат для UI-теста"):
        response = authorized_api_client.create_direct_chat(PHONE_PARTICIPANT)

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при создании direct-чата | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    chat = response.json()

    yield chat

    with allure.step("API cleanup: удалить direct-чат"):
        delete_response = authorized_api_client.delete_chat(chat["id"])

    if delete_response.status_code != 200:
        allure.attach(
            delete_response.text,
            name=f"Cleanup failed with HTTP {delete_response.status_code}",
            attachment_type=allure.attachment_type.TEXT,
        )


@pytest.fixture
def direct_chat_with_seed_message(created_direct_chat, authorized_api_client):
    message_text = f"AUTOTEST{uuid4().hex[:8]}"

    with allure.step("API: отправить уникальное сообщение"):
        message_response = authorized_api_client.send_message(
            created_direct_chat["id"],
            message_text,
        )

    assert message_response.status_code == 200, (
        f"Ожидание: HTTP 200 при отправке сообщения для поиска | "
        f"Факт: HTTP {message_response.status_code}, тело ответа: {message_response.text}"
    )

    return {
        "chat": created_direct_chat,
        "message_text": message_text,
    }


@pytest.fixture
def authorized_desktop_page(desktop_page, authorized_api_client):
    add_api_cookies_to_context(desktop_page.context, authorized_api_client)

    with allure.step("Открыть авторизованную desktop-страницу"):
        desktop_page.goto(BASE_URL)
        expect(desktop_page.get_by_role("navigation", name="Навигация")).to_be_visible()

    return desktop_page
