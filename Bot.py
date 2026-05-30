
import sys
from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio
import json

from datetime import datetime
from telegram import Bot


sys.stdout.reconfigure(encoding='utf-8')

with open("secret_info.json", "r") as f:
    data = json.load(f)
TOKEN = data.setdefault('token', "no token")
BOT_USERNAME = data.setdefault('bot_username', "no username")
print(TOKEN)
print(BOT_USERNAME)




bot = Bot(token=TOKEN)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Приветствую! Я Гриша, живу на колесах и люблю дорогу. Дальнобойщик по профессии и по духу. Давайте общаться!')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Без проблем, постараюсь помочь. Скажите, что конкретно нужно? В дороге всегда нужно быть готовым к любым ситуациям.')

async def klein_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    running = await toggle_running()
    await update.message.reply_text("Running: " + str(running))

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    processed: str = update.message.text.lower()
    answer = ""
    if 'привет' in processed:
        answer = 'Приветствую! Я Гриша, живу на колесах и люблю дорогу. Дальнобойщик по профессии и по духу. Давайте общаться!'
    else:
        answer = 'че?'
    print(update.message.chat_id)
    await update.message.reply_text(answer)

async def send_item(item):
    answer = item["name"] + "\n" + item["price"] + " EUR" + "\n" + item["location"] + ", " + item["delivery"] + "\n" + item["link"]
    await bot.send_message(chat_id=1558411879, text=answer)



async def toggle_running():
    with open("shared.json", "r") as f:
        data = json.load(f)
    running = data.setdefault('running', False)

    data['running'] = not running

    with open("shared.json", "w") as f:
        json.dump(data, f, indent=2)

    return not running

if __name__ == '__main__':
    print('starting...')
    app = Application.builder().token(TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('klein', klein_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Polls the bot
    print('polling...')
    app.run_polling(poll_interval=3)
