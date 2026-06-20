from pathlib import Path
from uuid import UUID

import allure
import pytest

from config.settings import (
    CODE,
    GROUP_ADD_MEMBER_PHONE,
    GROUP_CHAT_TITLE,
    GROUP_INITIAL_PARTICIPANTS_PHONES,
    NAME,
    PHONE,
    PHONE_PARTICIPANT,
    PHONE_PARTICIPANT_2,
    UPDATE_CHAT_TITLE,
)
from models import (
    AddChatMemberResponse,
    AdminWhitelistResponse,
    AttachmentInput,
    Chat,
    ChatUpdateResponse,
    ContactItem,
    FileRef,
    Message,
    UserProfile,
)


UPLOAD_FILE_PATH = Path(__file__).resolve().parents[1] / "files" / "test-upload.txt"


def assert_uuid(value, field_name):
    try:
        UUID(str(value))
    except (ValueError, TypeError):
        raise AssertionError(
            f"Ожидание: поле {field_name} содержит UUID | Факт: {field_name}={value!r}"
        )


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Авторизация")
@allure.story("Вход по коду")
@allure.severity(allure.severity_level.BLOCKER)
@allure.title("Успешная авторизация по коду")
@allure.description("""
🎯 Цель: проверить, что пользователь может успешно авторизоваться по номеру телефона и коду подтверждения.

📌 Предусловия:
- номер телефона существует на stage-окружении;
- код подтверждения валиден для указанного номера.

🧪 Шаги:
1. Отправить POST-запрос на эндпоинт /auth/login.
2. Передать в теле запроса номер телефона и код подтверждения.
3. Получить и разобрать JSON-ответ сервера.

✅ Ожидаемый результат::
- сервер возвращает HTTP 200;
- в ответе приходит ok=True;
- имя пользователя соответствует ожидаемому значению из тестовых настроек.
""")
def test_login(api_client, attach_api_info):
    with allure.step("Отправить запрос авторизации с валидным кодом"):
        response = api_client.login(PHONE, CODE)

        data = attach_api_info(
            response,
            request_body={
                "phone": PHONE,
                "code": "****"
            }
        )

    with allure.step("Проверить успешную авторизацию пользователя"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )
        assert data["ok"] is True, (
            f"Ожидание: ok=True | Факт: тело ответа={data}"
        )
        assert data["name"] == NAME, (
            f"Ожидание: name={NAME!r} | Факт: name={data['name']!r}"
        )


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Авторизация")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Авторизация")
@allure.story("Текущий пользователь")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение текущего авторизованного пользователя")
@allure.description("""
🎯 Цель: проверить, что авторизованная сессия возвращает данные текущего пользователя.

📌 Предусловия:
- пользователь успешно авторизован через фикстуру authorized_api_client;
- cookies авторизованной сессии сохранены в API-клиенте.

🧪 Шаги:
1. Отправить GET-запрос на эндпоинт /auth/me.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить признаки авторизованной сессии и данные пользователя.

✅ Ожидаемый результат::
- сервер возвращает HTTP 200;
- authenticated=True;
- id пользователя имеет формат UUID;
- номер телефона совпадает с ожидаемым номером из тестовых настроек.
""")
def test_get_auth_me(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные текущего пользователя"):
        response = authorized_api_client.get_auth_me()

        auth_me = attach_api_info(response)

    with allure.step("Проверить данные текущего пользователя"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )
        assert auth_me["authenticated"] is True, (
            f"Ожидание: authenticated=True | Факт: тело ответа={auth_me}"
        )
        assert_uuid(auth_me["id"], "auth_me.id")
        assert auth_me["phone"] == PHONE, (
            f"Ожидание: phone={PHONE!r} | Факт: phone={auth_me['phone']!r}"
        )


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Профиль")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить данные пользователя")
@allure.story("Текущий пользователь")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение данных авторизованного пользователя")
@allure.description("""
🎯 Цель: проверить получение профиля текущего авторизованного пользователя.

📌 Предусловия:
- пользователь успешно авторизован;
- cookies авторизованной сессии сохранены в API-клиенте.

🧪 Шаги:
1. Отправить GET-запрос на эндпоинт /users/me.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать ответ через Pydantic-модель UserProfile.
4. Проверить телефон и имя пользователя.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ соответствует модели UserProfile;
- phone совпадает с ожидаемым телефоном из тестовых настроек;
- name совпадает с ожидаемым именем из тестовых настроек.
""")
def test_get_user_profile(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные профиля"):
        response = authorized_api_client.get_user_profile()
        user_profile = attach_api_info(response)

    with allure.step("Проверить данные профиля"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        
        profile = UserProfile.model_validate(user_profile)

        assert profile.phone == PHONE, (
            f"Ожидание: phone={PHONE!r} | Факт: phone={profile.phone!r}"
        )
        assert profile.name == NAME, (
            f"Ожидание: name={NAME!r} | Факт: name={profile.name!r}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Админ")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить Whitelist")
@allure.story("Получить Whitelist")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Получение данных из Whitelist")
@allure.description("""
🎯 Цель: проверить получение административного whitelist пользователей.

📌 Предусловия:
- пользователь авторизован;
- пользователь имеет права администратора;
- в whitelist есть тестовый пользователь из настроек.

🧪 Шаги:
1. Отправить GET-запрос на эндпоинт /auth/admin/whitelist.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать ответ через Pydantic-модель AdminWhitelistResponse.
4. Найти текущего пользователя по номеру телефона.
5. Проверить имя пользователя и уникальность телефонов в whitelist.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ содержит список items;
- текущий пользователь найден в whitelist;
- имя текущего пользователя совпадает с ожидаемым;
- телефоны в whitelist не дублируются.
""")
def test_get_whitelist(authorized_api_client, attach_api_info):
    with allure.step("Запросить данные whitelist"):
        response = authorized_api_client.get_whitelist()
        data = attach_api_info(response)

    with allure.step("Проверить данные whitelist"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        whitelist = AdminWhitelistResponse.model_validate(data)
        items = whitelist.items
        assert items

        current_user = next(
            (item for item in items if item.phone == PHONE),
            None
        )

        assert current_user is not None, (
            f"Ожидание: пользователь {PHONE} есть в whitelist | Факт: whitelist={data}"
        )
        assert current_user.name == NAME, (
            f"Ожидание: name={NAME!r} | Факт: name={current_user.name!r}"
        )

        phones = [item.phone for item in items]

        assert len(phones) == len(set(phones)), (
            f"Ожидание: телефоны в whitelist уникальны | Факт: phones={phones}"
        )


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Контакты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Получить список контактов")
@allure.story("Получить список контактов")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получить список контактов")
@allure.description("""
🎯 Цель: проверить получение списка контактов текущего пользователя.

📌 Предусловия:
- пользователь авторизован;
- в whitelist есть пользователи, доступные как контакты.

🧪 Шаги:
1. Отправить GET-запрос на эндпоинт /contacts.
2. Получить и разобрать JSON-ответ сервера.
3. Провалидировать элементы ответа через Pydantic-модель ContactItem.
4. Проверить, что текущий пользователь не отображается у себя в контактах.
5. Проверить уникальность телефонов в списке контактов.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ является списком контактов;
- каждый контакт соответствует модели ContactItem;
- телефон текущего пользователя отсутствует в списке;
- телефоны контактов не дублируются.
""")
def test_get_contacts(authorized_api_client, attach_api_info):
    with allure.step("Проверить получения списка контактов"):
        response = authorized_api_client.get_contacts()
        data = attach_api_info(response)

    with allure.step("Проверить данные списка контактов"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        response_fields = [ContactItem.model_validate(field) for field in data]
        assert response_fields

        phones = [field.phone for field in response_fields]

        assert PHONE not in phones, (
            f"Ожидание: пользователь {PHONE} не должен быть у себя в контактах | Факт: контакты={data}"
        )

        assert len(phones) == len(set(phones)), (
            f"Ожидание: телефоны в контактах уникальны | Факт: phones={phones}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Создание группового чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Создание группового чата")
@allure.description("""
🎯 Цель: проверить создание группового чата с пользователем из тестовых данных.

📌 Предусловия:
- пользователь авторизован;
- номер собеседника добавлен в whitelist stage-окружения;
- после теста созданный чат удаляется фикстурой created_chat.

🧪 Шаги:
1. Создать групповой чат через фикстуру created_group_chat.
2. Провалидировать структуру ответа через Pydantic-модель Chat.
3. Проверить тип чата, роль текущего пользователя и данные собеседника.
4. Запросить список чатов текущего пользователя.
5. Проверить, что созданный чат появился в списке.

✅ Ожидаемый результат:
- создан чат с type=GROUP;
- роль текущего пользователя в чате равна ADMIN;
- созданный chat.id найден в списке чатов пользователя.
""")
def test_create_group_chat(created_group_chat, authorized_api_client, attach_api_info):
    with allure.step("Проверить данные созданного группового чата"):
        chat = Chat.model_validate(created_group_chat)
        chat_id = str(chat.id)

        assert chat.type == "GROUP", f"Ожидание: type='GROUP' | Факт: type={chat.type!r}"
        assert chat.role == "ADMIN", f"Ожидание: role='ADMIN' | Факт: role={chat.role!r}"
        assert chat.title == GROUP_CHAT_TITLE, f"Ожидание: title={GROUP_CHAT_TITLE!r} | Факт: title={chat.title!r}"
        expected_members_count = len(GROUP_INITIAL_PARTICIPANTS_PHONES) + 1

        assert len(chat.members) == expected_members_count, (
            f"Ожидание: количество участников равно {expected_members_count} с учетом создателя | "
            f"Факт: members={chat.members}"
        )
        
        member_phones = [member.phone for member in chat.members]

        assert PHONE in member_phones, (
            f"Ожидание: создатель группы {PHONE} есть в members | Факт: member_phones={member_phones}"
        )
        assert len(member_phones) == len(set(member_phones)), (
            f"Ожидание: телефоны участников группы уникальны | Факт: member_phones={member_phones}"
        )

        admin = next(
            (member for member in chat.members if member.phone == PHONE),
            None
        )

        assert admin is not None, (
            f"Ожидание: создатель группы {PHONE} есть в members | Факт: members={chat.members}"
        )
        assert admin.role == "ADMIN", (
            f"Ожидание: role='ADMIN' у создателя группы {PHONE} | Факт: role={admin.role!r}"
        )

        for phone in GROUP_INITIAL_PARTICIPANTS_PHONES:
            member = next(
                (member for member in chat.members if member.phone == phone),
                None
            )

            assert member is not None, f"Ожидание: участник {phone} есть в группе | Факт: members={chat.members}"
            assert member.role == "MEMBER", f"Ожидание: role='MEMBER' у участника {phone} | Факт: role={member.role!r}"

    with allure.step("Проверить наличие созданного групповго чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert chats_response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        )
        assert any(chat_item["id"] == chat_id for chat_item in chats), (
            f"Ожидание: созданный чат {chat_id} есть в списке чатов | Факт: список чатов={chats}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Изменение имени чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Изменение имени чата")
@allure.description("""
🎯 Цель: проверить изменение названия группового чата.

📌 Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- пользователь имеет право изменять параметры созданного чата.

🧪 Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить PATCH-запрос на эндпоинт /chats/{chatId}.
3. Передать новое название чата в теле запроса.
4. Провалидировать ответ через Pydantic-модель ChatUpdateResponse.
5. Запросить список чатов и проверить новое название в списке.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- chatId в ответе совпадает с id созданного чата;
- title в ответе совпадает с новым названием;
- в списке чатов отображается обновленное название.
""")
def test_update_chat_title(authorized_api_client, attach_api_info, created_group_chat):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
    with allure.step("Проверить изменение названия чата"):
        response = authorized_api_client.update_chat_title(
            chat_id,
            title=UPDATE_CHAT_TITLE
        )
        
        data = attach_api_info(response)
    
    with allure.step("Проверить данные ответа"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        response_fields = ChatUpdateResponse.model_validate(data)

        assert str(response_fields.chatId) == chat_id, (
            f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(response_fields.chatId)!r}"
        )
        assert response_fields.title == UPDATE_CHAT_TITLE, (
            f"Ожидание: title={UPDATE_CHAT_TITLE!r} | Факт: title={response_fields.title!r}"
        )

    with allure.step("Проверить изменение название в списке чатов"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert chats_response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        assert any(chat_item["id"] == chat_id and chat_item["title"] == UPDATE_CHAT_TITLE for chat_item in chats), (
            f"Ожидание: чат {chat_id} имеет title={UPDATE_CHAT_TITLE!r} | Факт: список чатов={chats}"
        )

@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Добавление участника в чат")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Добавление участника в чат")
@allure.description("""
🎯 Цель: проверить добавление участника в групповой чат.

📌 Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- номер добавляемого участника существует и разрешен на stage-окружении.

🧪 Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить POST-запрос на эндпоинт /chats/{chatId}/members.
3. Передать номер добавляемого участника в теле запроса.
4. Провалидировать ответ через Pydantic-модель AddChatMemberResponse.
5. Проверить id чата и роль добавленного участника.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- chatId в ответе совпадает с id созданного чата;
- добавленный пользователь получает роль MEMBER.
""")
def test_add_members(authorized_api_client, attach_api_info, created_group_chat):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
    with allure.step("Проверить добавление участника в чат"):
        response = authorized_api_client.add_chat_member(
            chat_id,
            phone_participant=GROUP_ADD_MEMBER_PHONE
        )
        
        data = attach_api_info(response)
    
    with allure.step("Проверить данные ответа"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        response_fields = AddChatMemberResponse.model_validate(data)

        assert str(response_fields.chatId) == chat_id, (
            f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(response_fields.chatId)!r}"
        )
        assert response_fields.role == "MEMBER", (
            f"Ожидание: role='MEMBER' | Факт: role={response_fields.role!r}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Удаление участника из чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Удаление участника из чата")
@allure.description("""
🎯 Цель: проверить удаление участника из группового чата.

📌 Предусловия:
- пользователь авторизован;
- групповой чат создан через фикстуру created_group_chat;
- удаляемый пользователь состоит в созданном групповом чате;
- у текущего пользователя есть право удалять участников.

🧪 Шаги:
1. Получить chat_id созданного группового чата.
2. Отправить DELETE-запрос на эндпоинт /chats/{chatId}/members/{userId}.
3. Передать user_id удаляемого участника в path-параметре.
4. Получить и разобрать JSON-ответ сервера.
5. Проверить успешный HTTP-статус ответа.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- участник удаляется из группового чата;
- запрос завершается без ошибки авторизации или доступа.
""")
def test_delete_members(authorized_api_client, attach_api_info, created_group_chat):
    with allure.step("Создать групповой чат"):
        chat_id = created_group_chat["id"]
        chat = Chat.model_validate(created_group_chat)
        target_phone = GROUP_INITIAL_PARTICIPANTS_PHONES[0]
        target_member = next(
            (member for member in chat.members if member.phone == target_phone),
            None
        )

        assert target_member is not None, (
            f"Ожидание: участник {target_phone} есть в группе | Факт: members={chat.members}"
        )

    with allure.step("Проверить удаление участника из чата"):
        response = authorized_api_client.delete_chat_member(
            chat_id,
            user_id=str(target_member.id)
        )
        
        data = attach_api_info(response)
    
    with allure.step("Проверить данные ответа"):
        assert response.status_code == 200, f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Файлы")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Файлы")
@allure.story("Загрузка файла")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Загрузка файла")
@allure.description("""
🎯 Цель: проверить загрузку файла через API.

📌 Предусловия:
- пользователь авторизован;
- тестовый файл существует в проекте.

🧪 Шаги:
1. Отправить POST-запрос на эндпоинт /files/upload.
2. Передать файл в multipart/form-data в поле file.
3. Получить и разобрать JSON-ответ сервера.
4. Провалидировать ответ через Pydantic-модель AttachmentInput.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ соответствует модели AttachmentInput;
- имя файла, MIME-тип и размер совпадают с отправленным файлом;
- в ответе есть key и url загруженного файла.
""")
def test_upload_file(authorized_api_client, attach_api_info):
    with allure.step("Загрузить файл"):
        response = authorized_api_client.upload_file(
            UPLOAD_FILE_PATH,
            mime_type="text/plain"
        )

        data = attach_api_info(response)

    with allure.step("Проверить данные загруженного файла"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )

        file_ref = AttachmentInput.model_validate(data)

        assert file_ref.filename == UPLOAD_FILE_PATH.name, (
            f"Ожидание: filename={UPLOAD_FILE_PATH.name!r} | Факт: filename={file_ref.filename!r}"
        )
        assert file_ref.mimeType == "text/plain", (
            f"Ожидание: mimeType='text/plain' | Факт: mimeType={file_ref.mimeType!r}"
        )
        assert file_ref.size == UPLOAD_FILE_PATH.stat().st_size, (
            f"Ожидание: size={UPLOAD_FILE_PATH.stat().st_size} | Факт: size={file_ref.size}"
        )
        assert file_ref.url, (
            f"Ожидание: url заполнен | Факт: url={file_ref.url!r}"
        )
        assert file_ref.key, (
            f"Ожидание: key заполнен | Факт: key={file_ref.key!r}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Аттачменты")
@allure.story("Отправка сообщения с файлом")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Отправка сообщения с аттачментом")
@allure.description("""
🎯 Цель: проверить, что пользователь может отправить сообщение с загруженным файлом.

📌 Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_chat;
- тестовый файл существует в проекте;
- после теста созданный чат удаляется фикстурой created_chat.

🧪 Шаги:
1. Получить chat_id из фикстуры created_chat.
2. Загрузить файл через эндпоинт /files/upload.
3. Провалидировать ответ загрузки через Pydantic-модель AttachmentInput.
4. Передать данные загруженного файла в attachments при создании сообщения.
5. Провалидировать ответ создания сообщения через Pydantic-модель Message.
6. Проверить связь сообщения с чатом и данные прикрепленного файла.

✅ Ожидаемый результат:
- сервер успешно загружает файл и возвращает HTTP 200;
- сервер успешно создает сообщение с аттачментом и возвращает HTTP 200;
- chatId сообщения совпадает с id созданного чата;
- в ответе сообщения есть один fileRef;
- filename, mimeType, size, key и url аттачмента совпадают с данными загруженного файла.
""")
def test_upload_attachment(authorized_api_client, attach_api_info, created_chat):
    chat_id = created_chat["id"]
    message_text = "Сообщение с файлом"

    with allure.step("Загрузить файл для аттачмента"):
        upload_response = authorized_api_client.upload_file(
            UPLOAD_FILE_PATH,
            mime_type="text/plain"
        )
        upload_data = attach_api_info(upload_response)

        assert upload_response.status_code == 200, (
            f"Ожидание: HTTP 200 при загрузке файла | "
            f"Факт: HTTP {upload_response.status_code}, тело ответа: {upload_response.text}"
        )

        uploaded_file = AttachmentInput.model_validate(upload_data)

    with allure.step("Отправить сообщение с аттачментом"):
        attachment = uploaded_file.model_dump(
            include={
                "key",
                "filename",
                "mimeType",
                "size",
                "url",
                "width",
                "height",
            }
        )
        request_body = {
            "text": message_text,
            "attachments": [attachment]
        }

        response = authorized_api_client.send_message(
            chat_id,
            text=message_text,
            attachments=[attachment]
        )
        data = attach_api_info(response, request_body=request_body)

    with allure.step("Проверить данные сообщения и аттачмента"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 при отправке сообщения с аттачментом | "
            f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )

        message = Message.model_validate(data)

        assert str(message.chatId) == chat_id, (
            f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(message.chatId)!r}"
        )
        assert message.text == message_text, (
            f"Ожидание: text={message_text!r} | Факт: text={message.text!r}"
        )
        assert message.isDeleted is False, (
            f"Ожидание: isDeleted=False | Факт: isDeleted={message.isDeleted!r}"
        )
        assert len(message.fileRefs) == 1, (
            f"Ожидание: у сообщения один аттачмент | Факт: fileRefs={message.fileRefs}"
        )

        attached_file = message.fileRefs[0]

        assert attached_file.filename == uploaded_file.filename, (
            f"Ожидание: filename={uploaded_file.filename!r} | Факт: filename={attached_file.filename!r}"
        )
        assert attached_file.mimeType == uploaded_file.mimeType, (
            f"Ожидание: mimeType={uploaded_file.mimeType!r} | Факт: mimeType={attached_file.mimeType!r}"
        )
        assert attached_file.size == uploaded_file.size, (
            f"Ожидание: size={uploaded_file.size} | Факт: size={attached_file.size}"
        )
        assert attached_file.key == uploaded_file.key, (
            f"Ожидание: key={uploaded_file.key!r} | Факт: key={attached_file.key!r}"
        )
        assert attached_file.url == uploaded_file.url, (
            f"Ожидание: url={uploaded_file.url!r} | Факт: url={attached_file.url!r}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Создание 1:1 чата")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Создание 1:1 чата")
@allure.description("""
🎯 Цель: проверить создание индивидуального 1:1 чата с пользователем из тестовых данных.

📌 Предусловия:
- пользователь авторизован;
- номер собеседника добавлен в whitelist stage-окружения;
- после теста созданный чат удаляется фикстурой created_chat.

🧪 Шаги:
1. Создать 1:1 чат через фикстуру created_chat.
2. Провалидировать структуру ответа через Pydantic-модель Chat.
3. Проверить тип чата, роль текущего пользователя и данные собеседника.
4. Запросить список чатов текущего пользователя.
5. Проверить, что созданный чат появился в списке.

✅ Ожидаемый результат:
- создан чат с type=DIRECT;
- роль текущего пользователя в чате равна MEMBER;
- в members присутствует один собеседник с ожидаемым телефоном;
- созданный chat.id найден в списке чатов пользователя.
""")
def test_create_direct_chat(created_chat, authorized_api_client, attach_api_info):
    with allure.step("Проверить данные созданного чата"):
        chat = Chat.model_validate(created_chat)
        chat_id = str(chat.id)

        assert chat.type == "DIRECT", (
            f"Ожидание: type='DIRECT' | Факт: type={chat.type!r}"
        )
        assert chat.role == "MEMBER", (
            f"Ожидание: role='MEMBER' | Факт: role={chat.role!r}"
        )
        assert len(chat.members) == 1, (
            f"Ожидание: в DIRECT-чате один собеседник | Факт: members={chat.members}"
        )

        member = chat.members[0]

        assert member.phone == PHONE_PARTICIPANT, (
            f"Ожидание: phone={PHONE_PARTICIPANT!r} | Факт: phone={member.phone!r}"
        )
        assert member.role == "MEMBER", (
            f"Ожидание: member.role='MEMBER' | Факт: member.role={member.role!r}"
        )

    with allure.step("Проверить наличие созданного чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert chats_response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        )
        assert any(chat_item["id"] == chat_id for chat_item in chats), (
            f"Ожидание: созданный чат {chat_id} есть в списке чатов | Факт: список чатов={chats}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Сообщения")
@allure.story("Отправка сообщения")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Отправка сообщения в 1:1 чат")
@allure.description("""
🎯 Цель: проверить отправку текстового сообщения в созданный 1:1 чат.

📌 Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_chat;
- после теста созданный чат удаляется фикстурой created_chat.

🧪 Шаги:
1. Получить chat_id из фикстуры created_chat.
2. Отправить POST-запрос на эндпоинт /chats/{chatId}/messages.
3. Передать в теле запроса текст сообщения.
4. Проверить статус ответа и основные поля созданного сообщения.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- id сообщения имеет формат UUID;
- chatId в ответе совпадает с id созданного чата;
- текст сообщения совпадает с отправленным;
- сообщение не удалено и не отредактировано;
- senderId имеет формат UUID;
- createdAt и updatedAt возвращаются строками.
""")
def test_send_message_direct_chat(authorized_api_client, attach_api_info, created_chat):
    chat_id = created_chat["id"]

    with allure.step("Отправить сообщение в созданный чат"):
        response = authorized_api_client.send_message(
            chat_id,
            text="Hello world!"
        )

        data = attach_api_info(response, request_body={"text": "Hello world!"})

    with allure.step("Проверить данные отправленного сообщения"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )
        assert_uuid(data["id"], "message.id")
        assert data["chatId"] == chat_id, (
            f"Ожидание: chatId={chat_id!r} | Факт: chatId={data.get('chatId')!r}"
        )
        assert data["text"] == "Hello world!", (
            f"Ожидание: text='Hello world!' | Факт: text={data.get('text')!r}"
        )
        assert data["isDeleted"] is False, (
            f"Ожидание: isDeleted=False | Факт: isDeleted={data.get('isDeleted')!r}"
        )
        assert data["editedAt"] is None, (
            f"Ожидание: editedAt=None | Факт: editedAt={data.get('editedAt')!r}"
        )
        assert data["threadRootMessageId"] is None, (
            f"Ожидание: threadRootMessageId=None | Факт: threadRootMessageId={data.get('threadRootMessageId')!r}"
        )
        assert data["forwardedFromMessageId"] is None, (
            f"Ожидание: forwardedFromMessageId=None | Факт: forwardedFromMessageId={data.get('forwardedFromMessageId')!r}"
        )
        assert_uuid(data["senderId"], "message.senderId")
        assert isinstance(data["createdAt"], str), (
            f"Ожидание: createdAt имеет тип str | Факт: тип={type(data.get('createdAt')).__name__}, значение={data.get('createdAt')!r}"
        )
        assert isinstance(data["updatedAt"], str), (
            f"Ожидание: updatedAt имеет тип str | Факт: тип={type(data.get('updatedAt')).__name__}, значение={data.get('updatedAt')!r}"
        )


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Удаление 1:1 чата")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Удаление 1:1 чата")
@allure.description("""
🎯 Цель: проверить удаление индивидуального 1:1 чата и отсутствие удаленного чата в списке.

📌 Предусловия:
- пользователь авторизован;
- номер собеседника добавлен в whitelist stage-окружения.

🧪 Шаги:
1. Создать 1:1 чат с тестовым собеседником.
2. Сохранить chat_id созданного чата.
3. Отправить DELETE-запрос на эндпоинт /chats/{chatId}.
4. Запросить актуальный список чатов.
5. Проверить, что удаленный чат отсутствует в списке.

✅ Ожидаемый результат:
- создание чата возвращает HTTP 200;
- удаление чата возвращает HTTP 200;
- в ответе на удаление приходит ok=True;
- удаленный chat_id не найден в списке чатов пользователя.
""")
def test_delete_direct_chat(authorized_api_client, attach_api_info):
    with allure.step("Создать 1:1 чат"):
        response = authorized_api_client.create_direct_chat(PHONE_PARTICIPANT_2)
        data = attach_api_info(response, request_body={"phone": PHONE_PARTICIPANT_2})

        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )

        chat_id = data["id"]

    with allure.step("Удалить созданный чат"):
        delete_response = authorized_api_client.delete_chat(chat_id)

        delete_data = attach_api_info(delete_response)

    with allure.step("Проверить успешное удаление чата"):
        assert delete_response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {delete_response.status_code}, тело ответа: {delete_response.text}"
        )
        assert delete_data["ok"] is True, (
            f"Ожидание: ok=True | Факт: тело ответа={delete_data}"
        )

    with allure.step("Проверить отсутствие удаленного чата в списке"):
        chats_response = authorized_api_client.get_chats()
        chats = attach_api_info(chats_response)

        assert chats_response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {chats_response.status_code}, тело ответа: {chats_response.text}"
        )
        assert all(chat["id"] != chat_id for chat in chats), (
            f"Ожидание: удаленный чат {chat_id} отсутствует в списке | Факт: список чатов={chats}"
        )


@pytest.mark.smoke
@allure.parent_suite("API Zapaska")
@allure.suite("Чаты")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Чаты")
@allure.story("Получение списка чатов")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Получение списка чатов")
@allure.description("""
🎯 Цель: проверить, что авторизованный пользователь может получить список своих чатов.

📌 Предусловия:
- пользователь авторизован через фикстуру authorized_api_client;
- список чатов запрашивается через фикстуру chats.

🧪 Шаги:
1. Отправить GET-запрос на эндпоинт /chats.
2. Получить и разобрать JSON-ответ сервера.
3. Проверить, что ответ является списком.
4. Если список не пустой, проверить формат id первого чата.

✅ Ожидаемый результат:
- сервер возвращает список;
- при наличии чатов chat.id имеет формат UUID.
""")
def test_get_list_chats(chats):
    with allure.step("Проверить структуру списка чатов"):
        assert isinstance(chats, list), (
            f"Ожидание: ответ имеет тип list | Факт: тип={type(chats).__name__}, значение={chats}"
        )
        if chats:
            chat = chats[0]
            assert_uuid(chat["id"], "chat.id")


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Сообщения")
@allure.story("История сообщений")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Загрузка истории сообщений")
@allure.description("""
🎯 Цель: проверить, что отправленное сообщение отображается в истории созданного чата.

📌 Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_chat;
- сообщение отправлено через фикстуру sent_message;
- после теста созданные тестовые данные удаляются фикстурами.

🧪 Шаги:
1. Получить chat_id созданного чата.
2. Получить message_id отправленного сообщения.
3. Отправить GET-запрос на эндпоинт /chats/{chatId}/messages с limit=10.
4. Провалидировать элементы ответа через Pydantic-модель Message.
5. Найти отправленное сообщение в истории.
6. Проверить id, chatId, текст, признак удаления, senderId и дату создания.

✅ Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ является списком сообщений;
- отправленное сообщение найдено в истории чата;
- поля найденного сообщения соответствуют данным созданного сообщения.
""")
def test_get_messages(authorized_api_client, attach_api_info, created_chat, sent_message):
    with allure.step("Получить id созданного чата"):
        chat_id = created_chat["id"]

    with allure.step("Получить id отправленного сообщения"):
        message_id = sent_message["id"]

    with allure.step("Запросить историю сообщений"):
        messages_response = authorized_api_client.get_messages(chat_id, limit=10)

        messages = attach_api_info(messages_response)

    with allure.step("Проверить найденное сообщение"):
        assert messages_response.status_code == 200, (
            f"Ожидание: HTTP 200 | Факт: HTTP {messages_response.status_code}, тело ответа: {messages_response.text}"
        )
        assert isinstance(messages, list), (
            f"Ожидание: ответ имеет тип list | Факт: тип={type(messages).__name__}, значение={messages}"
        )

        validated_messages = [Message.model_validate(item) for item in messages]

        message = next(
            (item for item in validated_messages if str(item.id) == message_id),
            None
        )

        assert message is not None, (
            f"Ожидание: сообщение {message_id} найдено в истории чата {chat_id} | Факт: сообщения={messages}"
        )
        assert str(message.id) == message_id, (
            f"Ожидание: message.id={message_id!r} | Факт: message.id={str(message.id)!r}"
        )
        assert str(message.chatId) == chat_id, (
            f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(message.chatId)!r}"
        )
        assert message.text == sent_message["text"], (
            f"Ожидание: text={sent_message['text']!r} | Факт: text={message.text!r}"
        )
        assert message.isDeleted is False, (
            f"Ожидание: isDeleted=False | Факт: isDeleted={message.isDeleted!r}"
        )
        assert message.senderId, (
            f"Ожидание: senderId заполнен | Факт: senderId={message.senderId!r}"
        )
        assert message.createdAt, (
            f"Ожидание: createdAt заполнен | Факт: createdAt={message.createdAt!r}"
        )
