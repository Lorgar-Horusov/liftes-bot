import sqlite3
import argparse
import logging
import sys

import keyring

from user_request import ClientInfo
from nacl.hash import blake2b
from nacl.encoding import HexEncoder
from nacl.secret import SecretBox
from nacl.utils import random
from keyring import errors

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, CallbackContext, CallbackQueryHandler

TOKEN = keyring.get_password('liftes_bot', 'telegram_token')
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


def generate_new_key() -> None:
    attempts = 5

    while attempts > 0:
        confirm = input('Are you sure you want to generate a new salt? '
                        'This will cause the database to become inaccessible y/n: ')
        if confirm.lower() == 'y':
            key = random(SecretBox.KEY_SIZE)
            keyring.set_password('liftes_bot', 'key', key.hex())
            logger.info('ключ сгенерирован и сохранен')
            logger.info(keyring.get_password('liftes_bot', 'key'))
            break
        elif confirm.lower() == 'n':
            sys.exit("Operation canceled by user.")
        else:
            attempts -= 1
            print(f"Invalid input. Please enter 'y' for yes or 'n' for no.\nAttempts left: {attempts}")

        if attempts == 0:
            logger.error("Maximum attempts reached. Exiting program.")
            sys.exit("Maximum attempts reached. Exiting program.")


def add_new_user(telegram_id: str, user_phone: str) -> None:
    key = keyring.get_password('liftes_bot', 'key')
    box = SecretBox(bytes.fromhex(key))
    user_id = telegram_id
    hex_user_id = blake2b(user_id.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    encrypted_user_number = box.encrypt(user_phone.encode('utf-8')).hex()
    with sqlite3.connect('users.db') as db:
        cursor = db.cursor()
        cursor.execute("INSERT INTO users VALUES (?, ?)", (hex_user_id, encrypted_user_number))
        db.commit()


def get_user_phone(telegram_id: str) -> str | None:
    try:
        key = keyring.get_password('liftes_bot', 'key')
    except keyring.errors.KeyringError as e:
        logger.error(e)
        return None

    box = SecretBox(bytes.fromhex(key))
    user_id = telegram_id
    hex_user_id = blake2b(user_id.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute("SELECT phone_number FROM users WHERE telegram_chat_id =?", (hex_user_id,))
    row = cursor.fetchone()
    db.close()

    if row is None:
        logger.info("Пользователь с таким ID не найден в базе данных")
        return None

    encrypted_phone_number = bytes.fromhex(row[0])
    phone_number = box.decrypt(encrypted_phone_number).decode('utf-8')
    return phone_number


def user_check(telegram_id: str) -> bool:
    user_id = telegram_id
    hex_user_id = blake2b(user_id.encode('utf-8'), encoder=HexEncoder).decode('utf-8')
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
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
        [InlineKeyboardButton("Мой адрес", callback_data='my_address')],
        [InlineKeyboardButton("Помощь", callback_data='help')],
        [InlineKeyboardButton("О боте", callback_data='about')]
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

    if query.data == 'my_address':
        await context.bot.send_chat_action(
            chat_id=update.effective_chat.id,
            action='typing'
        )
        phone = get_user_phone(str(update.effective_chat.id))
        if phone is not None:
            client_info = ClientInfo(phone)
            if client_info.access:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text=f'ваш адрес \n{client_info.address}')
            else:
                await context.bot.send_message(chat_id=update.effective_chat.id,
                                               text='Вашего адреса нет в базе данных, пожалуйста отправьте адрес\n(coming soon)')
        else:
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Пользователь с таким ID не найден в базе данных')
    elif query.data == 'help':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Это тестовая версия боиа, в будущем будут добавлены новые функции.')
    elif query.data == 'about':
        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text='Создан пользователем [Lorgar Horusov](https://github.com/Lorgar-Horusov/)',
                                       parse_mode='Markdown')


async def contact_handler(update: Update, context: CallbackContext) -> None:
    contact = update.message.contact
    phone_number = contact.phone_number
    add_new_user(str(update.effective_chat.id), phone_number)
    client_info = ClientInfo(phone_number)
    response_message = f'Здравствуйте {client_info.name}\nСпасибо за авторизацию!'
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
    parser.add_argument('-K', '--key', action='store_true', help='Generate salt')
    parser.add_argument('-Sb', '--start_bot', action='store_true', help='Launch bot')
    parser.add_argument('-Sa', '--set_api', help='Set API URL')
    parser.add_argument('-T', '--test', help='Phone number for test API')
    args = parser.parse_args()

    if args.create_table:
        create_table()
    elif args.key:
        generate_new_key()
    elif args.start_bot:
        start_bot()
    elif args.test:
        if args.test is None:
            print('Please use --test <phone number>')
            sys.exit()
        response = ClientInfo(args.test)
        print(f'address: {response.address}\n'
              f'name: {response.name}')
    elif args.set_api:
        if args.set_api is None:
            print('Please use --set_api <api url>')
            sys.exit()
        keyring.set_password('liftes_bot', 'liftes_api', args.set_api)
    else:
        print('No arguments provided')


if __name__ == '__main__':
    main()
