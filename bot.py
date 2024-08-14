import logging
import subprocess
import socket
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os

# Конфигурация логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функции команд бота
def get_server_info():
    try:
        # Получаем IP-адрес сервера
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Получаем информацию о времени работы
        uptime = subprocess.check_output("uptime -p", shell=True).decode('utf-8').strip()

        return f"IP-адрес сервера: {ip_address}\nВремя работы сервера: {uptime}"
    except Exception as e:
        logger.error(f"Ошибка при получении информации о сервере: {e}")
        return "Не удалось получить информацию о сервере."

def start(update: Update, context: CallbackContext) -> None:
    server_info = get_server_info()
    update.message.reply_text(f'Здравствуйте! Я бот для мониторинга ноды Allora.\n\n{server_info}')

def eth_price(update: Update, context: CallbackContext) -> None:
    try:
        result = subprocess.check_output("curl -s http://localhost:8000/inference/ETH", shell=True).decode('utf-8')
        update.message.reply_text(f"Цена ETH: {result}")
    except subprocess.CalledProcessError as e:
        update.message.reply_text("Не удалось получить цену ETH. Проверьте состояние ноды.")

def check_status(update: Update, context: CallbackContext) -> None:
    try:
        result = subprocess.check_output("docker inspect --format '{{json .State.Status}}' $(docker ps -q --filter name=worker)", shell=True).decode('utf-8').strip()
        update.message.reply_text(f"Статус контейнера worker: {result}")
    except subprocess.CalledProcessError as e:
        update.message.reply_text("Не удалось получить статус контейнера worker.")

def restart_container(update: Update, context: CallbackContext) -> None:
    try:
        status = subprocess.check_output("docker inspect --format '{{json .State.Status}}' $(docker ps -q --filter name=worker)", shell=True).decode('utf-8').strip()
        if status != "running":
            subprocess.check_call("docker restart worker", shell=True)
            update.message.reply_text("Контейнер worker перезапущен.")
        else:
            update.message.reply_text("Контейнер worker уже работает.")
    except subprocess.CalledProcessError as e:
        update.message.reply_text("Не удалось перезапустить контейнер worker.")

def uptime_container(update: Update, context: CallbackContext) -> None:
    try:
        result = subprocess.check_output("docker inspect --format '{{.State.StartedAt}}' $(docker ps -q --filter name=worker)", shell=True).decode('utf-8').strip()
        update.message.reply_text(f"Время работы контейнера worker: {result}")
    except subprocess.CalledProcessError as e:
        update.message.reply_text("Не удалось получить время работы контейнера worker.")

def main():
    # Загрузка токена из конфигурационного файла
    load_dotenv()
    TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    # Создание и запуск бота
    updater = Updater(token=TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('ETHprice', eth_price))
    dispatcher.add_handler(CommandHandler('checkstatus', check_status))
    dispatcher.add_handler(CommandHandler('restartcontainer', restart_container))
    dispatcher.add_handler(CommandHandler('uptimecontainer', uptime_container))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
