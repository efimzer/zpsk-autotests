import allure
import pytest

from models import AttachmentInput


@pytest.mark.regression
@allure.parent_suite("API Zapaska")
@allure.suite("Файлы")
@allure.sub_suite("Позитивные сценарии")
@allure.feature("Файлы")
@allure.story("Загрузка файла")
@allure.severity(allure.severity_level.NORMAL)
@allure.title("Загрузка файла")
@allure.description(
    """
Цель: проверить загрузку текстовых файлов через API с разным содержимым и именами.

Предусловия:
- пользователь авторизован;
- тестовый файл создается во временной директории pytest.
- тест параметризован файлами с латиницей, кириллицей, цифрами, спецсимволами и эмодзи в содержимом.

Шаги:
1. Отправить POST-запрос на эндпоинт /files/upload.
2. Передать параметризованный временный файл в multipart/form-data в поле file.
3. Получить и разобрать JSON-ответ сервера.
4. Провалидировать ответ через Pydantic-модель AttachmentInput.

Ожидаемый результат:
- сервер возвращает HTTP 200;
- ответ соответствует модели AttachmentInput;
- имя файла, MIME-тип и размер совпадают с текущим параметризованным файлом;
- в ответе есть key и url загруженного файла.
"""
)
@pytest.mark.parametrize(
    "file_name, file_content, mime_type",
    [
        pytest.param("upload-latin.txt", "Hello file", "text/plain", id="latin"),
        pytest.param("upload-cyrillic.txt", "Привет файл", "text/plain", id="cyrillic"),
        pytest.param("upload-digits-123.txt", "1234567890", "text/plain", id="digits"),
        pytest.param(
            "upload-special.txt", "!@#$%^&*()_+-=[]{}", "text/plain", id="special"
        ),
        pytest.param("upload-emoji.txt", "File 🙂🚀", "text/plain", id="emoji"),
    ],
)
def test_upload_file(
    authorized_api_client,
    attach_api_info,
    tmp_path,
    file_name,
    file_content,
    mime_type,
):
    upload_file_path = tmp_path / file_name
    upload_file_path.write_text(file_content, encoding="utf-8")

    with allure.step("Загрузить файл"):
        response = authorized_api_client.upload_file(
            upload_file_path, mime_type=mime_type
        )

        data = attach_api_info(response)

    with allure.step("Проверить данные загруженного файла"):
        assert (
            response.status_code == 200
        ), f"Ожидание: HTTP 200 | Факт: HTTP {response.status_code}, тело ответа: {response.text}"

        file_ref = AttachmentInput.model_validate(data)

        assert (
            file_ref.filename == upload_file_path.name
        ), f"Ожидание: filename={upload_file_path.name!r} | Факт: filename={file_ref.filename!r}"
        assert (
            file_ref.mimeType == mime_type
        ), f"Ожидание: mimeType={mime_type!r} | Факт: mimeType={file_ref.mimeType!r}"
        assert (
            file_ref.size == upload_file_path.stat().st_size
        ), f"Ожидание: size={upload_file_path.stat().st_size} | Факт: size={file_ref.size}"
        assert file_ref.url, f"Ожидание: url заполнен | Факт: url={file_ref.url!r}"
        assert file_ref.key, f"Ожидание: key заполнен | Факт: key={file_ref.key!r}"
