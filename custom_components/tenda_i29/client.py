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
        _LOGGER.debug("Tentativo di autenticazione sul Tenda i29 (%s)", self.host)
        
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
        try:
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
                _LOGGER.error("Autenticazione fallita: Nessun cookie ricevuto. Status: %s", response.status_code)
        except requests.exceptions.RequestException as err:
            _LOGGER.error("Errore di connessione durante l'autenticazione: %s", err)
            self.cookies = None

    def _api_post(self, payload, _retry=True):
        """Esegue una richiesta POST all'API del Tenda i29."""
        if self.cookies is None:
            self.auth()

        if self.cookies is None:
            return None

        headers = {"Content-Type": "application/json"}
        rand_param = f"{random.random()}"

        try:
            response = requests.post(
                f"http://{self.host}/goform/modules?{rand_param}",
                headers=headers,
                json=payload,
                cookies=self.cookies,
                verify=False,
                allow_redirects=False,
                timeout=10
            )

            if response.status_code != 200:
                if _retry:
                    _LOGGER.debug("Sessione scaduta, tento il ri-login...")
                    self.cookies = None
                    self.auth()
                    return self._api_post(payload, _retry=False)
                return None

            return response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError) as err:
            _LOGGER.warning("Errore nella richiesta al Tenda i29: %s", err)
            self.cookies = None
            return None

    def get_connected_devices(self):
        """Recupera la lista dei dispositivi connessi con tutti i dettagli."""
        json_response = self._api_post({"wifiClientList": {}})
        
        if json_response is None or "wifiClientList" not in json_response:
            _LOGGER.warning("Impossibile ottenere la lista dei dispositivi.")
            return {}

        devices = {}
        client_list = json_response.get("wifiClientList", [])
        _LOGGER.debug("Trovati %s dispositivi connessi", len(client_list))

        for device in client_list:
            mac = device.get("mac")
            if mac:
                connect_time_sec = int(device.get("connectTime", 0))
                hours = connect_time_sec // 3600
                minutes = (connect_time_sec % 3600) // 60
                
                if hours > 0:
                    connect_time_str = f"{hours}h {minutes}m"
                else:
                    connect_time_str = f"{minutes}m"

                signal_noise = device.get("signNoise", "")
                signal = ""
                if "/" in signal_noise:
                    signal = signal_noise.split("/")[0]

                devices[mac.lower()] = {
                    "ip": device.get("ip", ""),
                    "mac": mac,
                    "connect_time": connect_time_str,
                    "connect_time_sec": connect_time_sec,
                    "tx_rate": device.get("txRate", "0"),
                    "rx_rate": device.get("rxRate", "0"),
                    "signal": signal,
                    "signal_noise": signal_noise,
                }

        return devices
