class GlobalException(Exception):
    """Отсутствие необходимых переменных окружения."""


class APIResponseNot200Error(Exception):
    """Ответ API не равен 200."""


class EmptyValueKeyException(Exception):
    """Отсутствие значения ключа в ответе response."""


class FailureKeyException(Exception):
    """Отсутствие ключа homework в ответе response."""


class StatusNotFoundException(Exception):
    """Статус ответа не задокументирован."""

class FailResponseError(Exception):
    """Ошибка при выполнении запроса."""
