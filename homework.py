import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import (HomeworkBotException,
                        UnavailableEndpointError,
                        RequestEndpointError,
                        InvalidResponseError,
                        UnknownHomeworkStatusError,
                        )

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def check_tokens() -> bool:
    """Проверяет доступность переменных окружения."""
    return all((PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID))


def get_api_answer(timestamp: int) -> dict:
    """Делает запрос к эндпоинту API-сервиса."""
    payload = {'from_date': timestamp}
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            raise RequestEndpointError('Неверный ответ от API.')
        return response.json()
    except requests.ConnectionError:
        raise UnavailableEndpointError('API недоступен.')
    except requests.RequestException:
        raise RequestEndpointError('Сбой при запросе к API.')


def check_response(response: dict) -> None:
    """Проверяет ответ API на соответствие документации."""
    if not (
            isinstance(response, dict)
            and 'homeworks' in response and 'current_date' in response
            and isinstance(response['homeworks'], list)
    ):
        raise InvalidResponseError('Отсутствуют ожидаемые ключи в ответе API.')

    if not response['homeworks']:
        logger.debug('В ответе нет новых статусов.')


def parse_status(homework: dict) -> str:
    """Извлекает из информации о домашней работе статус этой работы."""
    if not ('homework_name' in homework and 'status' in homework):
        raise InvalidResponseError('Отсутствуют ожидаемые ключи в ответе API.')

    status = homework['status']

    if status not in HOMEWORK_VERDICTS:
        raise UnknownHomeworkStatusError()

    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot: telegram.Bot, message: str) -> None:
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение "{message}" отправлено в Telegram.')
    except telegram.TelegramError:
        logger.error('Сбой при отправке сообщения в Telegram.')


def main() -> None:
    """Основная логика работы бота."""
    if not check_tokens():
        logger.critical('Отсутствуют обязательные переменные окружения!')
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_api_error = None

    while True:
        try:
            response = get_api_answer(timestamp)
            check_response(response)
            for homework in response['homeworks']:
                send_message(bot, parse_status(homework))
            time.sleep(RETRY_PERIOD)
            timestamp = int(time.time())
        except HomeworkBotException as error:
            logger.error(error)
            if not isinstance(error, type(last_api_error)):
                last_api_error = error
                send_message(bot, str(error))


if __name__ == '__main__':
    main()
