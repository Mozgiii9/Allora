import logging
import subprocess
import socket
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
import os

# Конфигурация логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Функции команд бота
def get_server_info():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        uptime = subprocess.check_output("uptime -p", shell=True).decode('utf-8').strip()
        return f"🌐 *IP-адрес сервера:* `{ip_address}`\n⏱ *Время работы сервера:* `{uptime}`"
    except Exception as e:
        logger.error(f"Ошибка при получении информации о сервере: {e}")
        return "❌ Не удалось получить информацию о сервере."

async def start(update: Update, context) -> None:
    server_info = get_server_info()
    commands = (
        "⚙️ /ETHprice - *Узнать текущую цену ETH*\n"
        "🔍 /checkstatus - *Проверить статус контейнера*\n"
        "🔄 /restartcontainer - *Перезапустить контейнер*\n"
        "⏳ /uptimecontainer - *Показать время работы контейнера*\n"
    )
    await update.message.reply_text(
        f'👋 *Здравствуйте! Я бот для мониторинга ноды Allora.*\n\n'
        f'{server_info}\n\n'
        f'📜 *Доступные команды:*\n{commands}',
        parse_mode='Markdown'
    )

async def eth_price(update: Update, context) -> None:
    try:
        result = subprocess.check_output("curl -s http://localhost:8000/inference/ETH", shell=True).decode('utf-8')
        await update.message.reply_text(f"💰 *Цена ETH:* `{result}`", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить цену ETH. Проверьте состояние ноды.")

async def check_status(update: Update, context) -> None:
    try:
        result = subprocess.check_output("docker inspect --format '{{json .State.Status}}' $(docker ps -q --filter name=worker)", shell=True).decode('utf-8').strip()
        await update.message.reply_text(f"📦 *Статус контейнера worker:* `{result}`", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить статус контейнера worker.")

async def restart_container(update: Update, context) -> None:
    try:
        status = subprocess.check_output("docker inspect --format '{{json .State.Status}}' $(docker ps -q --filter name=worker)", shell=True).decode('utf-8').strip()
        if status != "running":
            subprocess.check_call("docker restart worker", shell=True)
            await update.message.reply_text("🔄 *Контейнер worker перезапущен.*", parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ *Контейнер worker уже работает.*", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось перезапустить контейнер worker.")

async def uptime_container(update: Update, context) -> None:
    try:
        result = subprocess.check_output("docker ps -f name=worker --format '{{.Status}}'", shell=True).decode('utf-8').strip()
        await update.message.reply_text(f"⏳ *Время работы контейнера worker:* `{result}`", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить время работы контейнера worker.")

def main():
    TOKEN = "TELEGRAM_BOT_TOKEN"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ETHprice", eth_price))
    app.add_handler(CommandHandler("checkstatus", check_status))
    app.add_handler(CommandHandler("restartcontainer", restart_container))
    app.add_handler(CommandHandler("uptimecontainer", uptime_container))

    app.run_polling()

if __name__ == '__main__':
    main()
