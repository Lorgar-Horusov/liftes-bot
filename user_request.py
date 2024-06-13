import requests
import logging
import keyring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('OwO logger')


class ClientInfo:
    def __init__(self, phone_number):
        self.phone_number = phone_number
        self._address = None
        self._name = None
        self._access = False
    
    @property
    def access(self):
        if not self._access:
            self._access = self._user_request().get('status')
        return self._access
    
    @property
    def address(self):
        if not self._address:
            self._address = self._user_request().get('addresses', [])
            if isinstance(self._address, list):
                self._address = '\n'.join(self._address)
        return self._address

    @property
    def name(self):
        if not self._name:
            self._name = self._user_request().get("fio")
        return self._name

    def _user_request(self) -> dict:
        data = {
            "label": "bot_auth",
            "phone": self.phone_number
        }
        url = keyring.get_password('liftes_bot', 'liftes_api')

        if not url:
            logger.error("Failed to retrieve URL from keyring")
            return {"error": "Failed to retrieve URL"}

        try:
            response = requests.post(url, data=data)
            response.raise_for_status()
            return response.json()

        except requests.exceptions.HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            return {"error": str(http_err)}

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            return {"error": str(e)}


if __name__ == '__main__':
    phone = input('phone: ')
    client_info = ClientInfo(phone)
    print(client_info.name)
    print(client_info.address)
