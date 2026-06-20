from uuid import UUID


def assert_uuid(value, field_name):
    try:
        UUID(str(value))
    except (ValueError, TypeError):
        raise AssertionError(
            f"Ожидание: поле {field_name} содержит UUID | Факт: {field_name}={value!r}"
        )
