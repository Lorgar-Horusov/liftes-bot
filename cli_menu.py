import keyring
import os
import logging
import secrets

from keyring import errors
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
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
    try:
        menu = inquirer.select(
            message="Выберите пункт",
            choices=["Настройки токена",
                     "Настройки соли",
                     "Настройки API (coming soon)",
                     "Создать БД",
                     "Назад"],
        ).execute()

        if menu == "Настройки токена":
            telegram_token_setting()
        elif menu == "Настройки соли":
            salt_setting()
        elif menu == "Создать БД":
            create_bd()
        elif menu == "Назад":
            main()
    except KeyboardInterrupt:
        clear()
        logger.error("экстренное закрытие программы")


def salt_setting() -> None:
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
            salt_setting()
        else:
            salt_setting()
    elif sub_menu == "Назад":
        setting()


def telegram_token_setting() -> None:
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
        telegram_token_setting()

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
            finally:
                telegram_token_setting()
        else:
            telegram_token_setting()
    elif sub_menu == "Назад":
        setting()


def create_bd() -> None:
    python_execute('main.py --create_table')


def main() -> None:
    clear()
    try:
        menu = inquirer.select(
            message="Выберите опцию",
            choices=[
                "Запуск бота",
                "Настройки",
                Choice(value=None, name='Выход'),
            ],
            default=None
        ).execute()

        if menu == "Запуск бота":
            python_execute('main.py --start_bot')
        elif menu == "Настройки":
            setting()

    except KeyboardInterrupt:
        clear()
        logger.error("экстренное закрытие программы")


if __name__ == '__main__':
    main()
