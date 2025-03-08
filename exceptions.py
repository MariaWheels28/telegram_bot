class GlobalException(Exception):
    """Отсутствие необходимых переменных окружения."""
    pass


class APIResponseException(Exception):
    """Сбой при подключении к API."""
    pass


class APIResponseNot200Error(Exception):
    """Ответ API не равен 200."""
    pass


class EmptyValueKeyException(Exception):
    """Отсутствие значения ключа в ответе response."""
    pass


class FailureKeyException(Exception):
    """Отсутствие ключа homework в ответе response."""
    pass


class StatusNotFoundException(Exception):
    """Статус ответа не задокументирован."""
    pass


class MessageSendingException(Exception):
    """Ошибка отправки сообщения."""
    pass
