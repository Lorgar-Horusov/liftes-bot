import requests
import logging
import keyring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


def user_request(phone: str) -> dict:
    data = {
        "label": "bot_auth",
        "phone": phone
    }
    url = keyring.get_password('liftes_bot', 'liftes_api')

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        logger.error(e)


if __name__ == '__main__':
    user_req = user_request(input('phone: '))
    print(user_req)
