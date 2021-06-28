import logging
import os
import time

import requests
import telegram
from dotenv import load_dotenv

load_dotenv()

PRAKTIKUM_TOKEN = os.getenv("PRAKTIKUM_TOKEN")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = telegram.Bot(token=TELEGRAM_TOKEN)

log_format = ('%(asctime)s  %(filename)s/%(funcName)s  '
              '%(levelname)s  %(message)s  %(name)s')
logging.basicConfig(
    level=logging.DEBUG,
    format=log_format,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler('bot.log')
file_handler.setFormatter(logging.Formatter(log_format))

logger.addHandler(file_handler)


def parse_homework_status(homework):
    homework_name = homework["homework_name"]
    if homework["status"] == "rejected":
        verdict = "К сожалению, в работе нашлись ошибки."
    else:
        verdict = "Ревьюеру всё понравилось, работа зачтена!"
    return f'У вас проверили работу "{homework_name}"!\n\n{verdict}'


def get_homeworks(current_timestamp):
    url = "https://praktikum.yandex.ru/api/user_api/homework_statuses/"
    headers = {"Authorization": f"OAuth {PRAKTIKUM_TOKEN}"}
    payload = {"from_date": current_timestamp}
    homework_statuses = requests.get(url, headers=headers, params=payload)
    return homework_statuses.json()


def send_message(message):
    return bot.send_message(CHAT_ID, message)


def main():
    logger.debug("Бот запущен")
    current_timestamp = int(time.time())

    while True:
        try:
            homeworks = get_homeworks(current_timestamp)
            current_timestamp = homeworks["current_date"]
            if homeworks["homeworks"]:
                homework = homeworks["homeworks"][0]
                message = parse_homework_status(homework)
                send_message(message)
                logger.info(
                    f'Сообщение "{message}" отправлено в чат {CHAT_ID}'
                )
            time.sleep(5 * 60)

        except Exception as e:
            err_message = f"Бот упал с ошибкой: {e}"
            logger.error(err_message)
            send_message(err_message)
            time.sleep(5)


if __name__ == "__main__":
    main()
