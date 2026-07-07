import base64
import json
import logging
from datetime import datetime
import requests
import random

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker import DeviceScanner
from homeassistant.components.device_tracker.legacy import async_process_config
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Sostituiamo il vecchio get_scanner con il setup moderno del config entry
async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
) -> bool:
    """Configura la piattaforma device_tracker basata sul Config Flow."""
    config = hass.data[DOMAIN][entry.entry_id]
    scanner = TendaI29DeviceScanner(config)
    
    # Home Assistant moderno registra i device tracker tramite lo scanner
    # che viene agganciato al sistema legacy di tracciamento interno.
    if scanner.is_initialized:
        # Questo dice a HA di usare lo scanner appena configurato
        hass.async_create_task(
            async_process_config(
                {DOMAIN: config}, scanner
            )
        )
        return True
    return False


class TendaI29DeviceScanner(DeviceScanner):
    def __init__(self, config):
        host = config[CONF_HOST]
        password = config[CONF_PASSWORD]
        self.is_initialized = False
        self.last_results = {}

        try:
            self.tenda_client = TendaI29Client(host, password)
            self._update_info()
            self.is_initialized = True
        except Exception as e:
            _LOGGER.error("Impossibile connettersi al Tenda i29: %s", e)

    def scan_devices(self):
        _LOGGER.debug("Scansione dispositivi Tenda i29...")
        self._update_info()
        # Ritorna una lista di MAC address attivi
        return list(self.last_results.keys())

    def get_device_name(self, device):
        # L'i29 non fornisce l'hostname, ritorniamo l'IP associato come fallback
        return self.last_results.get(device.lower())

    def _update_info(self):
        _LOGGER.debug("Caricamento client wireless da Tenda i29...")
        self.last_results = self.tenda_client.get_connected_devices()


class TendaI29Client:
    def __init__(self, host: str, password: str) -> None:
        self.host = host
        self.password = password
        self.cookies = None

    def auth(self):
        _LOGGER.debug("Tentativo di autenticazione sul Tenda i29")
        
        # Codifica la password in Base64 come richiesto dall'i29
        password_bytes = self.password.encode('utf-8')
        base64_password = base64.b64encode(password_bytes).decode('utf-8')

        # Genera il timestamp nel formato richiesto dal firmware (es. "2026;7;7;12;57;30")
        now = datetime.now()
        time_str = f"{now.year};{now.month};{now.day};{now.hour};{now.minute};{now.second}"

        payload = {
            "username": "admin",
            "password": base64_password,
            "logoff": False,
            "timeZone": 12, # Valore standard preso dal tuo payload
            "time": time_str
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
        }

        # Inviamo la richiesta di login a /modules
        response = requests.post(
            f"http://{self.host}/modules",
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

    def get_connected_devices(self):
        if self.cookies is None:
            self.auth()

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
        }

        # Usiamo un timestamp float per simulare il comportamento del browser (?0.xxxxx)
        rand_param = f"{random.random()}"

        try:
            response = requests.get(
                f"http://{self.host}/modules?{rand_param}",
                headers=headers,
                cookies=self.cookies,
                verify=False,
                allow_redirects=False,
                timeout=10
            )

            # Se scade la sessione (es. risponde con HTML o errore 401/302)
            if response.status_code != 200 or b"wifiClientList" not in response.content:
                _LOGGER.debug("Sessione scaduta o invalida, tento il ri-login...")
                self.cookies = None
                self.auth()
                return self.get_connected_devices()

            json_response = response.json()
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            self.cookies = None
            return {}

        devices = {}
        client_list = json_response.get("wifiClientList", [])

        for device in client_list:
            mac = device.get("mac")
            ip = device.get("ip")

            if mac:
                # Home Assistant gestisce i MAC address in minuscolo
                devices[mac.lower()] = ip

        return devices
