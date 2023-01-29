class HomeworkBotException(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class UnavailableEndpointError(HomeworkBotException):
    def __init__(self) -> None:
        super().__init__('Эндпойнт недоступен.')


class RequestEndpointError(HomeworkBotException):
    def __init__(self) -> None:
        super().__init__('Сбой при запросе к эндпоинту.')


class InvalidResponseError(HomeworkBotException, TypeError):
    def __init__(self) -> None:
        super().__init__('Отсутствуют ожидаемые ключи в ответе API.')


class UnknownHomeworkStatusError(HomeworkBotException):
    def __init__(self) -> None:
        super().__init__('Невалидный статус домашней работы.')