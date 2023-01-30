class HomeworkBotException(Exception):
    def __init__(self, message) -> None:
        super().__init__(message)


class UnavailableEndpointError(HomeworkBotException):
    pass


class RequestEndpointError(HomeworkBotException):
    pass


class InvalidResponseError(HomeworkBotException, TypeError):
    pass


class UnknownHomeworkStatusError(HomeworkBotException):
    pass