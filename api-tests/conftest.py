import json

import allure
import pytest

from clients.api_client import ApiClient
from config.settings import (
    BASE_URL,
    CODE,
    GROUP_CHAT_TITLE,
    GROUP_INITIAL_PARTICIPANTS_PHONES,
    PHONE,
    PHONE_PARTICIPANT,
)


@pytest.fixture
def api_client():
    return ApiClient(BASE_URL)


@pytest.fixture
def authorized_api_client(api_client, attach_api_info):
    login_response = api_client.login(PHONE, CODE)

    attach_api_info(
        login_response,
        request_body={
            "phone": PHONE,
            "code": "****",
        },
    )

    assert login_response.status_code == 200, (
        f"Ожидание: HTTP 200 при авторизации | "
        f"Факт: HTTP {login_response.status_code}, тело ответа: {login_response.text}"
    )

    return api_client


@pytest.fixture
def created_direct_chat(authorized_api_client, attach_api_info):
    response = authorized_api_client.create_direct_chat(PHONE_PARTICIPANT)
    chat = attach_api_info(response)

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при создании direct-чата | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    yield chat

    with allure.step("Очистка: удалить созданный direct-чат"):
        delete_response = authorized_api_client.delete_chat(chat["id"])
        attach_api_info(delete_response)

        assert delete_response.status_code == 200, (
            f"Ожидание: HTTP 200 при удалении direct-чата | "
            f"Факт: HTTP {delete_response.status_code}, тело ответа: {delete_response.text}"
        )


@pytest.fixture
def created_group_chat(authorized_api_client, attach_api_info):
    response = authorized_api_client.create_group_chat(
        title=GROUP_CHAT_TITLE,
        phone_participants=GROUP_INITIAL_PARTICIPANTS_PHONES,
    )
    chat = attach_api_info(response)

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при создании группового чата | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    yield chat

    with allure.step("Очистка: удалить созданный групповой чат"):
        delete_response = authorized_api_client.delete_chat(chat["id"])
        attach_api_info(delete_response)

        assert delete_response.status_code == 200, (
            f"Ожидание: HTTP 200 при удалении группового чата | "
            f"Факт: HTTP {delete_response.status_code}, тело ответа: {delete_response.text}"
        )


@pytest.fixture
def sent_direct_chat_message(
    authorized_api_client,
    attach_api_info,
    created_direct_chat,
):
    chat_id = created_direct_chat["id"]
    text = "Hello world!"

    response = authorized_api_client.send_message(chat_id, text=text)
    message = attach_api_info(response, request_body={"text": text})

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при отправке тестового сообщения | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    yield message

    with allure.step("Очистка: удалить отправленное сообщение"):
        delete_response = authorized_api_client.delete_message(message["id"])
        attach_api_info(delete_response)

        assert delete_response.status_code == 200, (
            f"Ожидание: HTTP 200 при удалении тестового сообщения | "
            f"Факт: HTTP {delete_response.status_code}, тело ответа: {delete_response.text}"
        )


@pytest.fixture
def chat_list(authorized_api_client, attach_api_info):
    response = authorized_api_client.get_chats()
    data = attach_api_info(response)

    assert response.status_code == 200, (
        f"Ожидание: HTTP 200 при получении списка чатов | "
        f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
    )

    return data


@pytest.fixture
def attach_api_info():
    def attach(response, request_body=None):
        request_info = f"""
Method: {response.request.method}
URL: {response.request.url}
"""

        allure.attach(
            request_info,
            name="Запрос",
            attachment_type=allure.attachment_type.TEXT,
        )

        if request_body is not None:
            allure.attach(
                json.dumps(request_body, indent=4, ensure_ascii=False),
                name="Тело запроса",
                attachment_type=allure.attachment_type.JSON,
            )

        try:
            response_body = response.json()
            allure.attach(
                json.dumps(response_body, indent=4, ensure_ascii=False),
                name="Тело ответа",
                attachment_type=allure.attachment_type.JSON,
            )
            return response_body
        except ValueError:
            allure.attach(
                response.text,
                name="Тело ответа",
                attachment_type=allure.attachment_type.TEXT,
            )
            return response.text

    return attach
