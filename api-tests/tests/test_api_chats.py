import allure
import pytest

from config.settings import (
    GROUP_ADD_MEMBER_PHONE,
    GROUP_CHAT_TITLE,
    GROUP_INITIAL_PARTICIPANTS_PHONES,
    PHONE,
    PHONE_PARTICIPANT,
    PHONE_PARTICIPANT_2,
)
from models import AddChatMemberResponse, Chat, ChatUpdateResponse
from helpers.assertions import assert_uuid


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Создание группового чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Создание группового чата")
@allure.description(
    """
Цель: проверить создание группового чата с участниками из тестовых данных.

Предусловия:
- пользователь авторизован;
- номера участников добавлены в whitelist stage-окружения;
- после теста созданный чат удаляется фикстурой created_group_chat.

Шаги:
1. Создать групповой чат через фикстуру created_group_chat.
2. Провалидировать структуру ответа через Pydantic-модель Chat.
3. Проверить тип чата, название, роль текущего пользователя и состав участников.
4. Запросить список чатов текущего пользователя.
5. Проверить, что созданный чат появился в списке.

Ожидаемый результат:
- создан чат с type=GROUP;
- роль текущего пользователя в чате равна ADMIN;
- название чата совпадает с тестовым значением;
- в members есть создатель и все участники из тестовых данных;
- созданный chat.id найден в списке чатов пользователя.
"""
)
def test_create_group_chat(created_group_chat, authorized_api_client, attach_api_info):
    with allure.step("Проверить данные созданного группового чата"):
        chat = Chat.model_validate(created_group_chat)
        chat_id = str(chat.id)

        assert (
            chat.type == "GROUP"
        ), f"Ожидание: type='GROUP' | Факт: type={chat.type!r}"
        assert (
            chat.role == "ADMIN"
        ), f"Ожидание: role='ADMIN' | Факт: role={chat.role!r}"
        assert (
            chat.title == GROUP_CHAT_TITLE
        ), f"Ожидание: title={GROUP_CHAT_TITLE!r} | Факт: title={chat.title!r}"
        expected_members_count = len(GROUP_INITIAL_PARTICIPANTS_PHONES) + 1

        assert len(chat.members) == expected_members_count, (
            f"Ожидание: количество участников равно {expected_members_count} с учетом создателя | "
            f"Факт: members={chat.members}"
        )

        member_phones = [member.phone for member in chat.members]

        assert (
            PHONE in member_phones
        ), f"Ожидание: создатель группы {PHONE} есть в members | Факт: member_phones={member_phones}"
        assert len(member_phones) == len(
            set(member_phones)
        ), f"Ожидание: телефоны участников группы уникальны | Факт: member_phones={member_phones}"

        admin = next((member for member in chat.members if member.phone == PHONE), None)

        assert (
            admin is not None
        ), f"Ожидание: создатель группы {PHONE} есть в members | Факт: members={chat.members}"
        assert (
            admin.role == "ADMIN"
        ), f"Ожидание: role='ADMIN' у создателя группы {PHONE} | Факт: role={admin.role!r}"

        for phone in GROUP_INITIAL_PARTICIPANTS_PHONES:
            member = next(
                (member for member in chat.members if member.phone == phone), None
            )

            assert (
                member is not None
            ), f"Ожидание: участник {phone} есть в группе | Факт: members={chat.members}"
            assert (
                member.role == "MEMBER"
            ), f"Ожидание: role='MEMBER' у участника {phone} | Факт: role={member.role!r}"

    with allure.step("Проверить наличие созданного группового чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert (
            chats_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        assert any(
            chat_item["id"] == chat_id for chat_item in chats
        ), f"Ожидание: созданный чат {chat_id} есть в списке чатов | Факт: список чатов={chats}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Изменение имени чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Изменение имени чата")
@allure.description(
    """
Цель: проверить изменение названия группового чата на разные допустимые значения.

Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- пользователь имеет право изменять параметры созданного чата.
- тест параметризован названиями с латиницей, кириллицей, цифрами, спецсимволами и эмодзи.

Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить PATCH-запрос на эндпоинт /chats/{chatId}.
3. Передать параметризованное новое название чата в теле запроса.
4. Провалидировать ответ через Pydantic-модель ChatUpdateResponse.
5. Запросить список чатов и проверить новое название в списке.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- chatId в ответе совпадает с id созданного чата;
- title в ответе совпадает с параметризованным названием;
- в списке чатов отображается это же обновленное название.
"""
)
@pytest.mark.parametrize(
    "new_title",
    [
        pytest.param("Updated chat title", id="latin"),
        pytest.param("Новое имя чата", id="cyrillic"),
        pytest.param("Chat 1234567890", id="digits"),
        pytest.param("Chat !@#$%^&*()", id="special"),
        pytest.param("Chat 🙂🚀", id="emoji"),
    ],
)
def test_update_chat_title(
    authorized_api_client,
    attach_api_info,
    created_group_chat,
    new_title,
):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
    with allure.step("Проверить изменение названия чата"):
        response = authorized_api_client.update_chat_title(chat_id, title=new_title)

        data = attach_api_info(response)

    with allure.step("Проверить данные ответа"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        response_fields = ChatUpdateResponse.model_validate(data)

        assert (
            str(response_fields.chatId) == chat_id
        ), f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(response_fields.chatId)!r}"
        assert (
            response_fields.title == new_title
        ), f"Ожидание: title={new_title!r} | Факт: title={response_fields.title!r}"

    with allure.step("Проверить изменение названия в списке чатов"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert (
            chats_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        assert any(
            chat_item["id"] == chat_id and chat_item["title"] == new_title
            for chat_item in chats
        ), f"Ожидание: чат {chat_id} имеет title={new_title!r} | Факт: список чатов={chats}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Добавление участника в чат")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Добавление участника в чат")
@allure.description(
    """
Цель: проверить добавление участника в групповой чат.

Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- номер добавляемого участника существует и разрешен на stage-окружении.

Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить POST-запрос на эндпоинт /chats/{chatId}/members.
3. Передать номер добавляемого участника в теле запроса.
4. Провалидировать ответ через Pydantic-модель AddChatMemberResponse.
5. Проверить id чата и роль добавленного участника.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- chatId в ответе совпадает с id созданного чата;
- добавленный пользователь получает роль MEMBER.
"""
)
def test_add_member_to_group_chat(
    authorized_api_client, attach_api_info, created_group_chat
):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
    with allure.step("Проверить добавление участника в чат"):
        response = authorized_api_client.add_chat_member(
            chat_id, phone_participant=GROUP_ADD_MEMBER_PHONE
        )

        data = attach_api_info(response)

    with allure.step("Проверить данные ответа"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        response_fields = AddChatMemberResponse.model_validate(data)

        assert (
            str(response_fields.chatId) == chat_id
        ), f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(response_fields.chatId)!r}"
        assert (
            response_fields.role == "MEMBER"
        ), f"Ожидание: role='MEMBER' | Факт: role={response_fields.role!r}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Удаление участника из чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Удаление участника из чата")
@allure.description(
    """
Цель: проверить удаление участника из группового чата.

Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- удаляемый пользователь состоит в созданном групповом чате;
- у текущего пользователя есть право удалять участников.

Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить DELETE-запрос на эндпоинт /chats/{chatId}/members/{userId}.
3. Передать user_id удаляемого участника в path-параметре.
4. Получить и разобрать JSON-ответ сервера.
5. Проверить успешный HTTP-статус ответа.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- запрос на удаление участника завершается без ошибки авторизации или доступа.
"""
)
def test_delete_member_from_group_chat(
    authorized_api_client, attach_api_info, created_group_chat
):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
        chat = Chat.model_validate(created_group_chat)
        target_phone = GROUP_INITIAL_PARTICIPANTS_PHONES[0]
        target_member = next(
            (member for member in chat.members if member.phone == target_phone), None
        )

        assert (
            target_member is not None
        ), f"Ожидание: участник {target_phone} есть в группе | Факт: members={chat.members}"

    with allure.step("Проверить удаление участника из чата"):
        response = authorized_api_client.delete_chat_member(
            chat_id, user_id=str(target_member.id)
        )

        attach_api_info(response)

    with allure.step("Проверить данные ответа"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Создание 1:1 чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Создание 1:1 чата")
@allure.description(
    """
Цель: проверить создание индивидуального 1:1 чата с пользователем из тестовых данных.

Предусловия:
- пользователь авторизован;
- номер собеседника добавлен в whitelist stage-окружения;
- после теста созданный чат удаляется фикстурой created_direct_chat.

Шаги:
1. Создать 1:1 чат через фикстуру created_direct_chat.
2. Провалидировать структуру ответа через Pydantic-модель Chat.
3. Проверить тип чата, роль текущего пользователя и данные собеседника.
4. Запросить список чатов текущего пользователя.
5. Проверить, что созданный чат появился в списке.

Ожидаемый результат:
- создан чат с type=DIRECT;
- роль текущего пользователя в чате равна MEMBER;
- в members присутствует один собеседник с ожидаемым телефоном;
- созданный chat.id найден в списке чатов пользователя.
"""
)
def test_create_direct_chat(
    created_direct_chat, authorized_api_client, attach_api_info
):
    with allure.step("Проверить данные созданного чата"):
        chat = Chat.model_validate(created_direct_chat)
        chat_id = str(chat.id)

        assert (
            chat.type == "DIRECT"
        ), f"Ожидание: type='DIRECT' | Факт: type={chat.type!r}"
        assert (
            chat.role == "MEMBER"
        ), f"Ожидание: role='MEMBER' | Факт: role={chat.role!r}"
        assert (
            len(chat.members) == 1
        ), f"Ожидание: в DIRECT-чате один собеседник | Факт: members={chat.members}"

        member = chat.members[0]

        assert (
            member.phone == PHONE_PARTICIPANT
        ), f"Ожидание: phone={PHONE_PARTICIPANT!r} | Факт: phone={member.phone!r}"
        assert (
            member.role == "MEMBER"
        ), f"Ожидание: member.role='MEMBER' | Факт: member.role={member.role!r}"

    with allure.step("Проверить наличие созданного чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert (
            chats_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        assert any(
            chat_item["id"] == chat_id for chat_item in chats
        ), f"Ожидание: созданный чат {chat_id} есть в списке чатов | Факт: список чатов={chats}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Удаление 1:1 чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Удаление 1:1 чата")
@allure.description(
    """
Цель: проверить удаление индивидуального 1:1 чата и отсутствие удаленного чата в списке.

Предусловия:
- пользователь авторизован;
- номер собеседника добавлен в whitelist stage-окружения.

Шаги:
1. Создать 1:1 чат с тестовым собеседником.
2. Сохранить chat_id созданного чата.
3. Отправить DELETE-запрос на эндпоинт /chats/{chatId}.
4. Запросить актуальный список чатов.
5. Проверить, что удаленный чат отсутствует в списке.

Ожидаемый результат:
- создание чата возвращает HTTP 200;
- удаление чата возвращает HTTP 200;
- в ответе на удаление приходит ok=True;
- удаленный chat_id не найден в списке чатов пользователя.
"""
)
def test_delete_direct_chat(authorized_api_client, attach_api_info):
    with allure.step("Создать 1:1 чат"):
        response = authorized_api_client.create_direct_chat(PHONE_PARTICIPANT_2)
        data = attach_api_info(response, request_body={"phone": PHONE_PARTICIPANT_2})

        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        chat_id = data["id"]

    with allure.step("Удалить созданный чат"):
        delete_response = authorized_api_client.delete_chat(chat_id)

        delete_data = attach_api_info(delete_response)

    with allure.step("Проверить успешное удаление чата"):
        assert (
            delete_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {delete_response.status_code}, тело ответа: {delete_response.text}"
        assert (
            delete_data["ok"] is True
        ), f"Ожидание: ok=True | Факт: тело ответа={delete_data}"

    with allure.step("Проверить отсутствие удаленного чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert (
            chats_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        assert all(
            chat["id"] != chat_id for chat in chats
        ), f"Ожидание: удаленный чат {chat_id} отсутствует в списке | Факт: список чатов={chats}"


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Получение списка чатов")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение списка чатов")
@allure.description(
    """
Цель: проверить, что авторизованный пользователь может получить список своих чатов.

Предусловия:
- пользователь авторизован через фикстуру authorized_api_client;
- список чатов запрашивается через фикстуру chat_list.

Шаги:
1. Отправить GET-запрос на эндпоинт /chat_list.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить, что ответ является списком.
4. Если список не пустой, проверить формат id первого чата.

Ожидаемый результат:
- сервер возвращает список;
- при наличии чатов chat.id имеет формат UUID.
"""
)
def test_get_chats(chat_list):
    with allure.step("Проверить структуру списка чатов"):
        assert isinstance(
            chat_list, list
        ), f"Ожидание: ответ имеет тип list | Факт: тип={type(chat_list).__name__}, значение={chat_list}"
        if chat_list:
            chat = chat_list[0]
            assert_uuid(chat["id"], "chat.id")
