class HomeworkBotException(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class UnavailableEndpointError(HomeworkBotException):
    """Ошибка недоступности API."""


class RequestEndpointError(HomeworkBotException):
    """Ошибка запроса к API."""


class InvalidResponseError(HomeworkBotException, TypeError):
    """Ошибка: некорректный ответ API."""


class UnknownHomeworkStatusError(HomeworkBotException):
    """Ошибка: неожиданный статус домашней работы."""
