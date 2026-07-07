import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components.device_tracker import DeviceScanner
from homeassistant.components.device_tracker.legacy import async_process_config
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .const import DOMAIN
from .client import TendaI29Client

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

