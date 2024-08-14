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
        "🔍 /checkstatus - *Проверить статус контейнеров*\n"
        "🔄 /restartcontainer - *Перезапустить контейнеры*\n"
        "⏳ /uptimecontainer - *Показать время работы контейнеров*\n"
        "🔔 /alert - *Получить оповещения о состоянии контейнеров*\n"
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
        await update.message.reply_text(f"💰 *Цена ETH: $* `{result}`", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить цену ETH. Проверьте состояние ноды.")

async def check_status(update: Update, context) -> None:
    try:
        containers = {
            'updater': 'basic-coin-prediction-node-updater',
            'inference': 'basic-coin-prediction-node-inference',
            'worker': 'alloranetwork/allora-offchain-node:latest'
        }
        status_text = ''
        for key, name in containers.items():
            result = subprocess.check_output(f"docker inspect --format '{{{{.State.Status}}}}' $(docker ps -q --filter ancestor={name})", shell=True).decode('utf-8').strip()
            status_text += f"📦 *Статус контейнера {key}:* `{result}`\n"
        await update.message.reply_text(status_text, parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить статус контейнеров.")

async def restart_container(update: Update, context) -> None:
    try:
        containers = ['basic-coin-prediction-node-updater', 'basic-coin-prediction-node-inference', 'alloranetwork/allora-offchain-node:latest']
        restarted = False
        for container in containers:
            status = subprocess.check_output(f"docker inspect --format '{{{{.State.Status}}}}' $(docker ps -q --filter ancestor={container})", shell=True).decode('utf-8').strip()
            if status != "running":
                subprocess.check_call(f"docker restart $(docker ps -q --filter ancestor={container})", shell=True)
                restarted = True
        if restarted:
            await update.message.reply_text("🔄 *Контейнеры перезапущены.*", parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ *Все контейнеры уже работают.*", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось перезапустить контейнеры.")

async def uptime_container(update: Update, context) -> None:
    try:
        containers = ['basic-coin-prediction-node-updater', 'basic-coin-prediction-node-inference', 'alloranetwork/allora-offchain-node:latest']
        uptime_text = ''
        for container in containers:
            result = subprocess.check_output(f"docker ps -f ancestor={container} --format '{{{{.Status}}}}'", shell=True).decode('utf-8').strip()
            uptime_text += f"⏳ *Время работы контейнера {container}:* `{result}`\n"
        await update.message.reply_text(uptime_text, parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось получить время работы контейнеров.")

async def alert(update: Update, context) -> None:
    try:
        containers = {
            'updater': 'basic-coin-prediction-node-updater',
            'inference': 'basic-coin-prediction-node-inference',
            'worker': 'alloranetwork/allora-offchain-node:latest'
        }
        alert_text = ''
        for key, name in containers.items():
            status = subprocess.check_output(f"docker inspect --format '{{{{.State.Status}}}}' $(docker ps -q --filter ancestor={name})", shell=True).decode('utf-8').strip()
            if status != 'running':
                alert_text += f"⚠️ *Контейнер {key} (image: {name}) не работает!*\n"
        if alert_text:
            await update.message.reply_text(alert_text, parse_mode='Markdown')
        else:
            await update.message.reply_text("✅ *Все контейнеры работают нормально.*", parse_mode='Markdown')
    except subprocess.CalledProcessError:
        await update.message.reply_text("❌ Не удалось проверить состояние контейнеров.")

def main():
    TOKEN = "TELEGRAM_BOT_TOKEN"

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ETHprice", eth_price))
    app.add_handler(CommandHandler("checkstatus", check_status))
    app.add_handler(CommandHandler("restartcontainer", restart_container))
    app.add_handler(CommandHandler("uptimecontainer", uptime_container))
    app.add_handler(CommandHandler("alert", alert))

    app.run_polling()

if __name__ == '__main__':
    main()
