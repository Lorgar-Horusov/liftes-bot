import sys

import keyring
import os
import logging
import secrets

from user_request import user_request
from keyring import errors
from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


def clear() -> None:
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


def python_execute(command: str) -> None:
    if os.name == 'nt':
        os.system(f'python {command}')
    elif os.name == 'posix':
        os.system(f'python3 {command}')


def setting() -> None:
    clear()
    menu = inquirer.select(
        message="Выберите пункт",
        choices=["Настройки токена",
                 "Настройки соли",
                 "Настройки API",
                 "Настройки языка (coming soon)",
                 "Создать БД",
                 "Назад"],
    ).execute()

    if menu == "Настройки токена":
        telegram_token_setting()
    elif menu == "Настройки соли":
        salt_setting()
    elif menu == "Создать БД":
        create_bd()
    elif menu == "Настройки API":
        api_setting()
    elif menu == "Назад":
        main()


def salt_setting() -> None:
    while True:
        sub_menu = inquirer.select(
            message="Выберите пункт",
            choices=["Сгенерировать соль",
                     "Назад"],
        ).execute()
        if sub_menu == "Сгенерировать соль":
            confirm = inquirer.confirm(
                message="Вы уверены, что хотите сгенерировать новую соль?\n"
                        "Это приведет к тому, что база данных станет недоступной.",
                default=False
            ).execute()
            if confirm:
                salt = secrets.token_hex(32)
                keyring.set_password('liftes_bot', 'salt', salt)
                logger.info('Соль сгенерирована и сохранена')
                break
            else:
                clear()
        elif sub_menu == "Назад":
            setting()


def telegram_token_setting() -> None:
    while True:
        sub_menu = inquirer.select(
            message="Выберите пункт",
            choices=["Новый токен",
                     "Удалить токен",
                     "Назад"],
        ).execute()
        if sub_menu == "Новый токен":
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

        elif sub_menu == "Удалить токен":
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

        elif sub_menu == "Назад":
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

        if sub_menu == "Новый API":
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

        elif sub_menu == "Удалить API":
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

        elif sub_menu == "Тестовый запрос API":
            phone = inquirer.text(
                message='Введите номер телефона'
            ).execute()
            response = user_request(phone)
            logger.info(response)

        elif sub_menu == "Назад":
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

        if menu == "Запуск бота":
            python_execute('main.py --start_bot')
        elif menu == "Настройки":
            setting()
        elif "Выход":
            sys.exit()

    except KeyboardInterrupt:
        clear()
        logger.error("экстренное закрытие программы")


if __name__ == '__main__':
    main()
