import os
import logging
import time
import requests
import datetime
import sys
from dotenv import load_dotenv
from telebot import TeleBot
from http import HTTPStatus

import exceptions


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
bot = TeleBot(token=TELEGRAM_TOKEN)
DATE_TIME = datetime.datetime(1970, 1, 1)


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filemode='w',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(
    handler
)


def check_tokens():
    """Проверка наличия токенов."""
    var_error = False
    for var in [TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PRACTICUM_TOKEN]:
        if var is None:
            var_error = True
            msg = f'Отсутствует обязательная переменная окружения: {var}'
            logging.critical(msg)
    if var_error:
        raise exceptions.GlobalException(
            'Недостаточное количество переменных окружения.')


def send_message(bot, message):
    """Отправка сообщения в Телеграм."""
    msg = f'Ошибка при отправке сообщения в Telegram: {message}'
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение успешно отправлено: {message}')
    except exceptions.MessageSendingException(msg):
        logger.error(msg)


def get_api_answer(timestamp):
    """Получить статус домашней работы."""
    payload = {'from_date': timestamp}

    msg = f'Сбой при подключении к эндпоинту: {ENDPOINT}'
    try:
        response = requests.get(ENDPOINT, headers=HEADERS, params=payload)
        if response.status_code != HTTPStatus.OK:
            msg = f'Код ответа API не равен 200: {response.status_code}'
            logger.error(msg)
            raise exceptions.APIResponseNot200Error(msg)
        return response.json()
    except exceptions.APIResponseException(msg):
        logger.error(msg)


def check_response(response):
    """Проверка статуса ответа домашней работы."""
    if response.get('homeworks') is None:
        msg = 'Отсутствие ключа homework в ответе response.'
        raise exceptions.FailureKeyException(msg)
    if response['homeworks'] == []:
        msg = 'Отсутствие значения homework в ответе response.'
        raise exceptions.EmptyValueKeyException(msg)

    status = response['homeworks'][0].get('status')
    if status is None:
        msg = 'Отсутствие ключа status в значении homework.'
        logger.error(msg)
        raise exceptions.FailureKeyException(msg)
    if status not in HOMEWORK_VERDICTS:
        msg = f'Hеожиданный статус домашней работы: {status}'
        logger.error(msg)
        raise exceptions.StatusNotFoundException(msg)
    return response['homeworks'][0]


def parse_status(homework):
    """Формирование сообщения о новом статусе домашней работы."""
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if status is None:
        msg = f'Пустое значение status: {status}'
        logger.error(msg)
        raise exceptions.EmptyValueError(msg)
    if homework_name is None:
        msg = f'Пустое значение homework_name: {homework_name}'
        logger.error(msg)
        raise exceptions.EmptyValueError(msg)
    verdict = HOMEWORK_VERDICTS[status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.mktime(DATE_TIME.timetuple()))
    previous_status = ''
    previous_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            status = homework['status']
            if homework and previous_status != status:
                message = parse_status(homework)
                send_message(bot, message)
                previous_status = homework['status']
            else:
                logger.debug(f'Статус домашней работы не изменен: {status}')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if previous_error != str(error):
                previous_error = str(error)
                send_message(bot, message)
            logger.critical(message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
