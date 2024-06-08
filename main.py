import sqlite3
import secrets
import argparse
import logging
import sys

import keyring

from dotenv import load_dotenv

from nacl.hash import blake2b
from nacl.encoding import HexEncoder
from user_request import user_request

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, CallbackContext, CallbackQueryHandler

load_dotenv()
TOKEN = keyring.get_password('liftes_bot', 'telegram_token')
SALT = keyring.get_password('liftes_bot', 'salt')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


def create_table() -> None:
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    try:
        logger.info('creating table...')
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (telegram_chat_id TEXT, phone_number TEXT)""")
        db.commit()
        db.close()
        logger.info('table created')
    except Exception as e:
        logger.error(f'Error creating table: {e}')
    finally:
        db.close()


def generate_salt() -> None:
    attempts = 5
    while True:
        for i in range(5):
            confirm = input('Are you sure you want to generate a new salt?'
                            ' This will cause the database to become inaccessible y/n: ')
            if confirm.lower() == 'y':
                salt = secrets.token_hex(32)
                keyring.set_password('liftes_bot', 'salt', salt)
                logger.info('Соль сгенерирована и сохранена')
                break
            elif confirm.lower() == 'n':
                sys.exit()
            else:
                attempts -= 1
                print(f"Invalid input. Please enter 'y' for yes or 'n' for no.\nAttempts {attempts}")
        break


def add_new_user(telegram_id: str, user_phone: str) -> None:
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    user_id = telegram_id + SALT
    user_number = user_phone + SALT
    hex_user_id = blake2b(user_id.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    hex_user_number = blake2b(user_number.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    cursor.execute("SELECT 1 FROM users WHERE telegram_chat_id = ?", (hex_user_id,))
    if cursor.fetchone() is None:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (hex_user_id, hex_user_number))
        db.commit()
    db.close()


def user_check(telegram_id: str) -> bool:
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    user_id = telegram_id + SALT
    hex_user_id = blake2b(user_id.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    cursor.execute("SELECT EXISTS (SELECT 1 FROM users WHERE telegram_chat_id =?)", (hex_user_id,))
    result = cursor.fetchone()[0]
    db.close()
    return result


async def start(update: Update, context: CallbackContext) -> None:
    if not user_check(str(update.effective_chat.id)):
        keyboard = [
            [KeyboardButton("Отправить номер телефона", request_contact=True)]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Пожалуйста, отправьте ваш номер телефона.',
                                       reply_markup=reply_markup)

    else:
        await show_main_menu(update, context)


async def show_main_menu(update: Update, context: CallbackContext) -> None:
    welcome_text = "Добро пожаловать! Пожалуйста, выберите одну из следующих опций:"

    keyboard = [
        [InlineKeyboardButton("Сделать заказ", callback_data='order')],
        [InlineKeyboardButton("Помощь", callback_data='help')],
        [InlineKeyboardButton("О нас", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=welcome_text,
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'order':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Для заказа, пожалуйста, опишите ваш заказ.')
    elif query.data == 'help':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Вы можете зарегистрироваться или сделать заказ, используя кнопки ниже.')
    elif query.data == 'about':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Мы - команда, предоставляющая лучшие услуги!')


async def contact_handler(update: Update, context: CallbackContext) -> None:
    contact = update.message.contact
    phone_number = contact.phone_number
    add_new_user(str(update.effective_chat.id), phone_number)
    response_message = 'Спасибо за авторизацию!'
    await context.bot.send_message(chat_id=update.effective_chat.id, text=response_message,
                                   reply_markup=ReplyKeyboardRemove())
    await show_main_menu(update, context)


def start_bot() -> None:
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.CONTACT, contact_handler))

    print('Бот запущен!')
    app.run_polling()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('-Ct', '--create_table', action='store_true', help='Create table')
    parser.add_argument('-S', '--salt', action='store_true', help='Generate salt')
    parser.add_argument('-Sb', '--start_bot', action='store_true', help='Launch bot')
    parser.add_argument('-Sa', '--set_api', help='Set API URL')
    parser.add_argument('-T', '--test', help='Phone number for test API')
    args = parser.parse_args()

    if args.create_table:
        create_table()
    elif args.salt:
        generate_salt()
    elif args.start_bot:
        start_bot()
    elif args.test:
        if args.test is None:
            print('Please use --test <phone number>')
            sys.exit()
        response = user_request(args.test)
        print(response)
    elif args.set_api:
        if args.set_api is None:
            print('Please use --set_api <api url>')
            sys.exit()
        keyring.set_password('liftes_bot', 'liftes_api', args.set_api)
    else:
        print('No arguments provided')


if __name__ == '__main__':
    main()
