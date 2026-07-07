import logging

from homeassistant.components.device_tracker.config_entry import ScannerEntity, SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configura la piattaforma device_tracker basata sul Config Flow."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    tracked_macs = set()

    @callback
    def add_new_entities():
        """Aggiunge nuove entità in base ai MAC rilevati."""
        new_entities = []
        if coordinator.data:
            for mac, info in coordinator.data.items():
                if mac not in tracked_macs:
                    tracked_macs.add(mac)
                    new_entities.append(TendaScannerEntity(coordinator, mac, info, entry.entry_id))
            
        if new_entities:
            async_add_entities(new_entities)

    # Ascolta gli aggiornamenti per trovare nuovi dispositivi
    coordinator.async_add_listener(add_new_entities)
    
    # Aggiungi i dispositivi iniziali
    add_new_entities()

    return True


class TendaScannerEntity(CoordinatorEntity, ScannerEntity):
    """Rappresenta un dispositivo tracciato sul Tenda i29."""

    def __init__(self, coordinator, mac_address, device_info, entry_id):
        """Inizializza l'entità tracker."""
        super().__init__(coordinator)
        self._mac_address = mac_address
        self._initial_ip = device_info.get("ip", "")
        self._attr_unique_id = f"tenda_i29_{mac_address}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    def _get_device_data(self):
        """Ritorna i dati aggiornati del dispositivo dal coordinator."""
        if self.coordinator.data and self._mac_address in self.coordinator.data:
            return self.coordinator.data[self._mac_address]
        return None

    @property
    def mac_address(self) -> str:
        """Ritorna l'indirizzo MAC del dispositivo."""
        return self._mac_address

    @property
    def ip_address(self) -> str:
        """Ritorna l'indirizzo IP del dispositivo."""
        data = self._get_device_data()
        if data:
            return data.get("ip", self._initial_ip)
        return self._initial_ip

    @property
    def name(self) -> str:
        """Ritorna il nome del dispositivo con MAC e IP."""
        return f"Tenda {self._mac_address[-8:].upper()} ({self.ip_address})"

    @property
    def is_connected(self) -> bool:
        """Ritorna True se il dispositivo è connesso."""
        return self._get_device_data() is not None

    @property
    def source_type(self) -> SourceType:
        """Ritorna il tipo di sorgente (Router)."""
        return SourceType.ROUTER

    @property
    def extra_state_attributes(self):
        """Attributi extra visibili nella scheda dell'entità."""
        data = self._get_device_data()
        if data:
            return {
                "mac_address": self._mac_address,
                "ip_address": data.get("ip", ""),
                "connesso_da": data.get("connect_time", ""),
                "velocita_tx": f"{data.get('tx_rate', '0')} Mbps",
                "velocita_rx": f"{data.get('rx_rate', '0')} Mbps",
                "segnale": data.get("signal", ""),
                "segnale_rumore": data.get("signal_noise", ""),
            }
        return {
            "mac_address": self._mac_address,
            "ip_address": self._initial_ip,
        }
