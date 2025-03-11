import datetime
import logging
import os
import sys
import time
from http import HTTPStatus

import requests
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiException

import exceptions


load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')


RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
DATE_TIME = datetime.datetime(1970, 1, 1)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)


def check_tokens():
    """Проверка наличия токенов."""
    GLOBAL_VALUE = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID),
    )
    empty_values = []
    for key, var in GLOBAL_VALUE:
        if var is None:
            msg = f'Отсутствует обязательная переменная окружения: {key}'
            empty_values.append(key)
            logging.critical(msg)
    if empty_values:
        raise exceptions.GlobalException(
            f'Недостаточное количество переменных окружения: {empty_values}')


def send_message(bot, message):
    """Отправка сообщения в Телеграм."""
    msg = f'Ошибка при отправке сообщения в Telegram: {message}'
    success = False
    try:
        logger.debug('Начало отправки сообщения в Telegram...')
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.debug(f'Сообщение успешно отправлено: {message}')
        success = True
    except requests.RequestException as ex:
        logger.error(f'{msg} (ошибка сети): {ex}')
    except ApiException as ex:
        logger.error(f'{msg} (ошибка API Telegram): {ex}')

    return success


def get_api_answer(timestamp):
    """Получить статус домашней работы."""
    payload = {'from_date': timestamp}

    msg = f'Сбой при подключении к эндпоинту: {ENDPOINT}'
    main_params = {
        'ENDPOINT': ENDPOINT,
        'HEADERS': HEADERS,
        'params': payload
    }
    try:
        logger.info(f'Программа начала запрос: {main_params}')
        response = requests.get(
            main_params['ENDPOINT'],
            headers=main_params['HEADERS'],
            params=main_params['params']
        )
    except requests.RequestException as ex:
        logger.error(f'{msg}: {ex}')
        raise exceptions.FailResponseError(f'{msg}: {ex}')

    if response.status_code != HTTPStatus.OK:
        msg = f'Код ответа API не равен 200: {response.status_code}'
        raise exceptions.APIResponseNot200Error(msg)

    return response.json()


def check_response(response):
    """Проверка статуса ответа домашней работы."""
    if not isinstance(response, dict):
        raise TypeError(
            'В ответе API данные не в виде словаря.'
            f'Тип объекта response: {type(response)}'
        )
    if response.get('homeworks') is None:
        msg = 'Отсутствие ключа homework в ответе response.'
        raise exceptions.FailureKeyException(msg)

    homeworks = response['homeworks']
    if not isinstance(homeworks, list):
        raise TypeError(
            'В ответе API данные не в виде списка.'
            f'Тип ключа homework: {type(homeworks)}'
        )

    return homeworks


def parse_status(homework):
    """Формирование сообщения о новом статусе домашней работы."""
    status = homework.get('status')
    homework_name = homework.get('homework_name')
    if status is None:
        msg = 'Пустое значение status.'
        raise exceptions.EmptyValueError(msg)
    if homework_name is None:
        msg = 'Пустое значение homework_name.'
        raise exceptions.EmptyValueError(msg)
    if status not in HOMEWORK_VERDICTS:
        msg = f'Hеожиданный статус домашней работы: {status}'
        raise exceptions.StatusNotFoundException(msg)
    verdict = HOMEWORK_VERDICTS[status]

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.mktime(DATE_TIME.timetuple()))
    previous_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                homework = homeworks[0]
                message = parse_status(homework)
                success_sending = send_message(bot, message)
                if success_sending:
                    timestamp = response.get('current_date', timestamp)
                    previous_error = ''
            else:
                logger.debug('Статус домашней работы не изменен.')

        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if previous_error != str(error):
                previous_error = str(error)
                send_message(bot, message)
            logger.critical(message)
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filemode='w',
        format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
    )
    main()
