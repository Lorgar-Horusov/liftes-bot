import argparse
import logging
import sys

import keyring

from user_request import ClientInfo

from database import user_check, get_user_phone, add_new_user, create_table, generate_new_key, error_logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, \
    filters, CallbackContext, CallbackQueryHandler

TOKEN = keyring.get_password('liftes_bot', 'telegram_token')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


async def start(update: Update, context: CallbackContext) -> None:
    try:
        if not user_check(str(update.effective_chat.id)):
            keyboard = [
                [KeyboardButton("Отправить номер телефона", request_contact=True)]
            ]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            await context.bot.send_message(chat_id=update.effective_chat.id,
                                           text='Пожалуйста, отправьте ваш номер телефона.',
                                           reply_markup=reply_markup)
    except Exception as e:
        error_logging(e)

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
                                               text='Вашего адреса нет в базе данных, пожалуйста отправьте адрес\n'
                                                    '(coming soon)')
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
