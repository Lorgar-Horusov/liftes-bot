import sys

import keyring
import os
import logging

from user_request import ClientInfo
from keyring import errors
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator
from nacl.secret import SecretBox
from nacl.utils import random

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


def clear() -> None:
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


def pause() -> None:
    if os.name == 'nt':
        os.system('pause')
    elif os.name == 'posix':
        os.system('read -n1 -r -p "Нажмите любую клавишу, чтобы продолжить..." key')


def python_execute(command: str) -> None:
    if os.name == 'nt':
        os.system(f'python {command}')
    elif os.name == 'posix':
        os.system(f'python3 {command}')


def setting() -> None:
    while True:
        clear()
        menu = inquirer.select(
            message="Выберите пункт",
            choices=["Настройки токена",
                     "Настройки ключа",
                     "Настройки API",
                     "Настройки языка (coming soon)",
                     "Создать БД",
                     "Назад"],
        ).execute()
        match menu:
            case "Настройки токена":
                telegram_token_setting()
            case "Настройки ключа":
                key_setting()
            case "Создать БД":
                create_bd()
            case "Настройки API":
                api_setting()
            case _:
                main()


def generate_new_key() -> None:
    key = random(SecretBox.KEY_SIZE)
    keyring.set_password('liftes_bot', 'key', key.hex())
    logger.info('ключ сгенерирован и сохранен\nВаш ключ')
    logger.info(keyring.get_password('liftes_bot', 'key'))


def key_setting() -> None:
    while True:
        sub_menu = inquirer.select(
            message="Выберите пункт",
            choices=["Сгенерировать ключ",
                     "Ввести ключ",
                     "Назад"],
        ).execute()
        match sub_menu:
            case "Сгенерировать ключ":
                confirm = inquirer.confirm(
                    message="Вы уверены, что хотите сгенерировать новый ключ?\n"
                            "Это приведет к тому, что база данных станет недоступной.",
                    default=False
                ).execute()
                if confirm:
                    generate_new_key()
                    break
                else:
                    clear()

            case "Ввести ключ":
                clear()
                old_key = keyring.get_password('liftes_bot', 'key')
                if old_key is None:
                    old_key = ''
                new_key = inquirer.secret(
                    message='Введите ключ',
                    default=old_key,
                    validate=EmptyInputValidator()
                ).execute()
                keyring.set_password('liftes_bot', 'key', new_key)

            case _:
                setting()


def telegram_token_setting() -> None:
    while True:
        sub_menu = inquirer.select(
            message="Выберите пункт",
            choices=["Новый токен",
                     "Удалить токен",
                     "Назад"],
        ).execute()
        match sub_menu:
            case "Новый токен":
                clear()
                old_token = keyring.get_password('liftes_bot', 'telegram_token')
                if old_token is None:
                    old_token = ''
                new_token = inquirer.secret(
                    message="пожалуйста, введите токен",
                    default=old_token,
                    validate=EmptyInputValidator()
                ).execute()

                keyring.set_password('liftes_bot', 'telegram_token', new_token)
                logger.info('Токен сохранен')

            case "Удалить токен":
                clear()
                confirm = inquirer.confirm(
                    message='Вы уверены?',
                    default=False
                ).execute()

                if confirm:
                    try:
                        keyring.delete_password('liftes_bot', 'telegram_token')
                        logger.info('Токен удален')

                    except keyring.errors.PasswordDeleteError as e:
                        logger.error(f'Ошибка при удалении токена {e}')

            case _:
                setting()


def create_bd() -> None:
    python_execute('main.py --create_table')


def api_setting() -> None:
    while True:
        sub_menu = inquirer.select(
            message="Выберите пункт",
            choices=[
                "Новый API",
                "Удалить API",
                "Тестовый запрос API",
                "Назад"
            ]
        ).execute()

        match sub_menu:
            case "Новый API":
                clear()
                old_api = keyring.get_password('liftes_bot', 'liftes_api')

                if old_api is None:
                    old_api = ''
                new_api = inquirer.text(
                    message='Введите новый API',
                    default=old_api,
                    validate=EmptyInputValidator()
                ).execute()
                keyring.set_password('liftes_bot', 'liftes_api', new_api)
                logger.info('API Установлен')

            case "Удалить API":
                clear()
                confirm = inquirer.confirm(
                    message='Вы уверены?',
                    default=False
                ).execute()

                if confirm:
                    try:
                        keyring.delete_password('liftes_bot', 'liftes_api')
                        logger.info('Пароль удален')
                    except keyring.errors.PasswordDeleteError as e:
                        logger.error(e)

            case "Тестовый запрос API":
                phone = inquirer.text(
                    message='Введите номер телефона'
                ).execute()
                clear()
                client_info = ClientInfo(phone)
                logger.info(f'Адрес: {client_info.address}\nИмя: {client_info.name}')
                pause()

            case _:
                setting()


def main() -> None:
    clear()
    try:
        menu = inquirer.select(
            message="Выберите опцию",
            choices=[
                "Запуск бота",
                "Настройки",
                "Выход",
            ],
        ).execute()

        match menu:
            case "Запуск бота":
                python_execute('main.py --start_bot')
            case "Настройки":
                setting()
            case _:
                sys.exit()

    except KeyboardInterrupt:
        clear()
        logger.error("экстренное закрытие программы")


if __name__ == '__main__':
    main()
