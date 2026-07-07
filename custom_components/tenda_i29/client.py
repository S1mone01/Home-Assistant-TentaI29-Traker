import base64
import json
import logging
from datetime import datetime
import requests
import random

_LOGGER = logging.getLogger(__name__)

class TendaI29Client:
    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.cookies = None

    def auth(self):
        _LOGGER.debug("Tentativo di autenticazione sul Tenda i29")
        
        password_bytes = self.password.encode('utf-8')
        base64_password = base64.b64encode(password_bytes).decode('utf-8')

        now = datetime.now()
        time_str = f"{now.year};{now.month};{now.day};{now.hour};{now.minute};{now.second}"

        payload = {
            "sysLogin": {
                "username": "admin",
                "password": base64_password,
                "logoff": False,
                "timeZone": 12,
                "time": time_str
            }
        }

        headers = {
            "Content-Type": "application/json",
        }

        rand_param = f"{random.random()}"
        response = requests.post(
            f"http://{self.host}/goform/modules?{rand_param}",
            headers=headers,
            json=payload,
            verify=False,
            allow_redirects=False,
            timeout=10
        )
        
        if response.cookies:
            self.cookies = response.cookies
            _LOGGER.debug("Autenticazione riuscita, cookie salvati.")
        else:
            _LOGGER.error("Autenticazione fallita: Nessun cookie ricevuto.")

    def get_connected_devices(self, _retry=True):
        if self.cookies is None:
            self.auth()

        if self.cookies is None:
            _LOGGER.warning("Impossibile autenticarsi sul Tenda i29, salto il polling.")
            return {}

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
        }

        rand_param = f"{random.random()}"

        try:
            response = requests.get(
                f"http://{self.host}/goform/modules?module1=wifiClientList&{rand_param}",
                headers=headers,
                cookies=self.cookies,
                verify=False,
                allow_redirects=False,
                timeout=10
            )

            if response.status_code != 200 or b"wifiClientList" not in response.content:
                if _retry:
                    _LOGGER.debug("Sessione scaduta o invalida, tento il ri-login...")
                    self.cookies = None
                    self.auth()
                    return self.get_connected_devices(_retry=False)
                _LOGGER.warning("Impossibile ottenere la lista dei dispositivi dopo il ri-login.")
                return {}

            json_response = response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as err:
            _LOGGER.warning("Errore nella richiesta al Tenda i29: %s", err)
            self.cookies = None
            return {}

        devices = {}
        client_list = json_response.get("wifiClientList", [])

        for device in client_list:
            mac = device.get("mac")
            ip = device.get("ip")

            if mac:
                devices[mac.lower()] = ip

        return devices
