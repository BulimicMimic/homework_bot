import logging
import os
import sys
import time

import requests
import telegram
from dotenv import load_dotenv

from exceptions import *

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

ENDPOINT_ERRORS = [
    UnavailableEndpointError,
    RequestEndpointError,
    InvalidResponseError,
    UnknownHomeworkStatusError,
]

logging.basicConfig(
    stream=sys.stdout,
    format='%(asctime)s, %(levelname)s, %(message)s'
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def check_tokens():
    """Проверяет доступность переменных окружения."""
    return PRACTICUM_TOKEN and TELEGRAM_TOKEN and TELEGRAM_CHAT_ID


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    try:
        payload = {'from_date': timestamp}
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != 200:
            raise RequestEndpointError()
        return response.json()
    except requests.ConnectionError:
        raise UnavailableEndpointError()
    except requests.RequestException:
        raise RequestEndpointError()


def check_response(response):
    """Проверяет ответ API на соответствие документации."""
    if not ('homeworks' in response and 'current_date' in response):
        raise InvalidResponseError()
    if not isinstance(response['homeworks'], list):
        raise InvalidResponseError()
    if not response['homeworks']:
        logger.debug('В ответе нет новых статусов.')


def parse_status(homework):
    """Извлекает из информации о домашней работе статус этой работы."""
    if 'homework_name' not in homework:
        raise InvalidResponseError()
    if homework['status'] not in HOMEWORK_VERDICTS:
        raise UnknownHomeworkStatusError()
    homework_name = homework['homework_name']
    verdict = HOMEWORK_VERDICTS[homework['status']]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def send_message(bot, message):
    """Отправляет сообщение в Telegram чат."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение "{message}" отправлено в Telegram.')
    except telegram.TelegramError:
        logger.error('Сбой при отправке сообщения в Telegram.')


def main():
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
            if error not in ENDPOINT_ERRORS:
                send_message(bot, error)
            else:
                if not isinstance(error, type(last_api_error)):
                    last_api_error = error
                    send_message(bot, error)


if __name__ == '__main__':
    main()
