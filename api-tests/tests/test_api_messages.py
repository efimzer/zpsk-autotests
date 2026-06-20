from pathlib import Path

import allure
import pytest

from models import AttachmentInput, Message
from helpers.assertions import assert_uuid


UPLOAD_FILE_PATH = Path(__file__).resolve().parents[1] / "files" / "test-upload.txt"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Аттачменты")
@allure.story("Отправка сообщения с файлом")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Отправка сообщения с аттачментом")
@allure.description(
    """
Цель: проверить, что пользователь может отправить сообщение с загруженным файлом.

Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_direct_chat;
- тестовый файл существует в проекте;
- после теста созданный чат удаляется фикстурой created_direct_chat.

Шаги:
1. Получить chat_id из фикстуры created_direct_chat.
2. Загрузить файл через эндпоинт /files/upload.
3. Провалидировать ответ загрузки через Pydantic-модель AttachmentInput.
4. Передать данные загруженного файла в attachments при создании сообщения.
5. Провалидировать ответ создания сообщения через Pydantic-модель Message.
6. Проверить связь сообщения с чатом и данные прикрепленного файла.

Ожидаемый результат:
- сервер успешно загружает файл и возвращает HTTP 200;
- сервер успешно создает сообщение с аттачментом и возвращает HTTP 200;
- chatId сообщения совпадает с id созданного чата;
- в ответе сообщения есть один fileRef;
- filename, mimeType, size, key и url аттачмента совпадают с данными загруженного файла.
"""
)
def test_send_message_with_attachment(
    authorized_api_client, attach_api_info, created_direct_chat
):
    chat_id = created_direct_chat["id"]
    message_text = "Сообщение с файлом"

    with allure.step("Загрузить файл для аттачмента"):
        upload_response = authorized_api_client.upload_file(
            UPLOAD_FILE_PATH, mime_type="text/plain"
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
        request_body = {"text": message_text, "attachments": [attachment]}

        response = authorized_api_client.send_message(
            chat_id, text=message_text, attachments=[attachment]
        )
        data = attach_api_info(response, request_body=request_body)

    with allure.step("Проверить данные сообщения и аттачмента"):
        assert response.status_code == 200, (
            f"Ожидание: HTTP 200 при отправке сообщения с аттачментом | "
            f"Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        )

        message = Message.model_validate(data)

        assert (
            str(message.chatId) == chat_id
        ), f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(message.chatId)!r}"
        assert (
            message.text == message_text
        ), f"Ожидание: text={message_text!r} | Факт: text={message.text!r}"
        assert (
            message.isDeleted is False
        ), f"Ожидание: isDeleted=False | Факт: isDeleted={message.isDeleted!r}"
        assert (
            len(message.fileRefs) == 1
        ), f"Ожидание: у сообщения один аттачмент | Факт: fileRefs={message.fileRefs}"

        attached_file = message.fileRefs[0]

        assert (
            attached_file.filename == uploaded_file.filename
        ), f"Ожидание: filename={uploaded_file.filename!r} | Факт: filename={attached_file.filename!r}"
        assert (
            attached_file.mimeType == uploaded_file.mimeType
        ), f"Ожидание: mimeType={uploaded_file.mimeType!r} | Факт: mimeType={attached_file.mimeType!r}"
        assert (
            attached_file.size == uploaded_file.size
        ), f"Ожидание: size={uploaded_file.size} | Факт: size={attached_file.size}"
        assert (
            attached_file.key == uploaded_file.key
        ), f"Ожидание: key={uploaded_file.key!r} | Факт: key={attached_file.key!r}"
        assert (
            attached_file.url == uploaded_file.url
        ), f"Ожидание: url={uploaded_file.url!r} | Факт: url={attached_file.url!r}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Сообщения")
@allure.story("Отправка сообщения")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Отправка сообщения в 1:1 чат")
@allure.description(
    """
Цель: проверить отправку текстового сообщения в созданный 1:1 чат с разными вариантами текста.

Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_direct_chat;
- после теста созданный чат удаляется фикстурой created_direct_chat.
- тест параметризован сообщениями с латиницей, кириллицей, цифрами, спецсимволами и эмодзи.

Шаги:
1. Получить chat_id из фикстуры created_direct_chat.
2. Отправить POST-запрос на эндпоинт /chats/{chatId}/messages.
3. Передать в теле запроса параметризованный текст сообщения.
4. Проверить статус ответа и основные поля созданного сообщения.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- id сообщения имеет формат UUID;
- chatId в ответе совпадает с id созданного чата;
- текст сообщения совпадает с текущим параметризованным значением;
- сообщение не удалено и не отредактировано;
- senderId имеет формат UUID;
- createdAt и updatedAt возвращаются строками.
"""
)
@pytest.mark.parametrize(
    "message_text",
    [
        pytest.param("Hello world!", id="latin"),
        pytest.param("Привет мир!", id="cyrillic"),
        pytest.param("Message 1234567890", id="digits"),
        pytest.param("Message !@#$%^&*()", id="special"),
        pytest.param("Message 🙂🚀", id="emoji"),
    ],
)
def test_send_message_direct_chat(
    authorized_api_client,
    attach_api_info,
    created_direct_chat,
    message_text,
):
    chat_id = created_direct_chat["id"]

    with allure.step("Отправить сообщение в созданный чат"):
        response = authorized_api_client.send_message(chat_id, text=message_text)

        data = attach_api_info(response, request_body={"text": message_text})

    with allure.step("Проверить данные отправленного сообщения"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"
        assert_uuid(data["id"], "message.id")
        assert (
            data["chatId"] == chat_id
        ), f"Ожидание: chatId={chat_id!r} | Факт: chatId={data.get('chatId')!r}"
        assert (
            data["text"] == message_text
        ), f"Ожидание: text={message_text!r} | Факт: text={data.get('text')!r}"
        assert (
            data["isDeleted"] is False
        ), f"Ожидание: isDeleted=False | Факт: isDeleted={data.get('isDeleted')!r}"
        assert (
            data["editedAt"] is None
        ), f"Ожидание: editedAt=None | Факт: editedAt={data.get('editedAt')!r}"
        assert (
            data["threadRootMessageId"] is None
        ), f"Ожидание: threadRootMessageId=None | Факт: threadRootMessageId={data.get('threadRootMessageId')!r}"
        assert (
            data["forwardedFromMessageId"] is None
        ), f"Ожидание: forwardedFromMessageId=None | Факт: forwardedFromMessageId={data.get('forwardedFromMessageId')!r}"
        assert_uuid(data["senderId"], "message.senderId")
        assert isinstance(
            data["createdAt"], str
        ), f"Ожидание: createdAt имеет тип str | Факт: тип={type(data.get('createdAt')).__name__}, значение={data.get('createdAt')!r}"
        assert isinstance(
            data["updatedAt"], str
        ), f"Ожидание: updatedAt имеет тип str | Факт: тип={type(data.get('updatedAt')).__name__}, значение={data.get('updatedAt')!r}"


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Сообщения")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Сообщения")
@allure.story("История сообщений")
@allure.severity(allure.severity_level.CRITICAL)
@allure.title("Загрузка истории сообщений")
@allure.description(
    """
Цель: проверить, что отправленное сообщение отображается в истории созданного чата.

Предусловия:
- пользователь авторизован;
- 1:1 чат создан через фикстуру created_direct_chat;
- сообщение отправлено через фикстуру sent_direct_chat_message;
- после теста созданные тестовые данные удаляются фикстурами.

Шаги:
1. Получить chat_id созданного чата.
2. Получить message_id отправленного сообщения.
3. Отправить GET-запрос на эндпоинт /chats/{chatId}/messages с limit=10.
4. Провалидировать элементы ответа через Pydantic-модель Message.
5. Найти отправленное сообщение в истории.
6. Проверить id, chatId, текст, признак удаления, senderId и дату создания.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ является списком сообщений;
- отправленное сообщение найдено в истории чата;
- поля найденного сообщения соответствуют данным созданного сообщения.
"""
)
def test_get_direct_chat_messages(
    authorized_api_client,
    attach_api_info,
    created_direct_chat,
    sent_direct_chat_message,
):
    with allure.step("Получить id созданного чата"):
        chat_id = created_direct_chat["id"]

    with allure.step("Получить id отправленного сообщения"):
        message_id = sent_direct_chat_message["id"]

    with allure.step("Запросить историю сообщений"):
        messages_response = authorized_api_client.get_messages(chat_id, limit=10)

        messages = attach_api_info(messages_response)

    with allure.step("Проверить найденное сообщение"):
        assert (
            messages_response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {messages_response.status_code}, тело ответа: {messages_response.text}"
        assert isinstance(
            messages, list
        ), f"Ожидание: ответ имеет тип list | Факт: тип={type(messages).__name__}, значение={messages}"

        validated_messages = [Message.model_validate(item) for item in messages]

        message = next(
            (item for item in validated_messages if str(item.id) == message_id), None
        )

        assert (
            message is not None
        ), f"Ожидание: сообщение {message_id} найдено в истории чата {chat_id} | Факт: сообщения={messages}"
        assert (
            str(message.id) == message_id
        ), f"Ожидание: message.id={message_id!r} | Факт: message.id={str(message.id)!r}"
        assert (
            str(message.chatId) == chat_id
        ), f"Ожидание: chatId={chat_id!r} | Факт: chatId={str(message.chatId)!r}"
        assert (
            message.text == sent_direct_chat_message["text"]
        ), f"Ожидание: text={sent_direct_chat_message['text']!r} | Факт: text={message.text!r}"
        assert (
            message.isDeleted is False
        ), f"Ожидание: isDeleted=False | Факт: isDeleted={message.isDeleted!r}"
        assert (
            message.senderId
        ), f"Ожидание: senderId заполнен | Факт: senderId={message.senderId!r}"
        assert (
            message.createdAt
        ), f"Ожидание: createdAt заполнен | Факт: createdAt={message.createdAt!r}"
