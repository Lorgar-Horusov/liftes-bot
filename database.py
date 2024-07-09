import sqlite3
import logging
import keyring
import traceback
import sys

from datetime import date, datetime
from nacl.hash import blake2b
from nacl.encoding import HexEncoder
from nacl.secret import SecretBox
from nacl.utils import random
from keyring import errors

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


def create_error_logging_table() -> None:
    with sqlite3.connect('error_logger.db') as db:
        cursor = db.cursor()
        try:
            logger.info('creating table')
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            error_type TEXT,
            error_message TEXT,
            error_traceback TEXT,
            error_time TEXT,
            log_date TEXT
            )
            ''')
            db.commit()
        except Exception as e:
            logger.error(e)


def error_logging(error_info: Exception) -> None:
    error_message = str(error_info)
    error_type = type(error_info).__name__
    error_traceback = traceback.format_exc()
    current_day = date.today().strftime('%Y-%m-%d')
    current_time = datetime.now().strftime('%H:%M')
    with sqlite3.connect('error_logger.db') as db:
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO logs ('
                           'error_type, '
                           'error_message, '
                           'error_traceback, '
                           'error_time, '
                           'log_date'
                           ') VALUES (?, ?, ?, ?, ?)',
                           (error_type, error_message, error_traceback, current_time, current_day))
        except Exception as e:
            logger.error(e)


def error_test() -> None:
    try:
        t = 5 / 0  # error
        print(t)
    except Exception as e:
        log = e
        error_logging(log)


def get_logs(time_from: str, time_to: str):
    conn = sqlite3.connect("error_logger.db")
    cursor = conn.cursor()
    query = "SELECT * FROM logs WHERE log_date BETWEEN ? AND ?"
    cursor.execute(query, (time_from, time_to))
    rows = cursor.fetchall()
    conn.close()
    logs = []

    for row in rows:
        log = {
            "error_id": row[0],
            "error_type": row[1],
            "error_message": row[2],
            "error_traceback": row[3],
            "error_time": row[4],
            "date": row[5]
        }
        logs.append(log)
    return logs


if __name__ == '__main__':
    # print(get_logs('2024-06-14', '2024-06-17'))
    # create_error_logging_table()
    error_test()
