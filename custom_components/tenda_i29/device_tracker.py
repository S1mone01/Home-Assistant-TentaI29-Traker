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
            for mac, ip in coordinator.data.items():
                if mac not in tracked_macs:
                    tracked_macs.add(mac)
                    new_entities.append(TendaScannerEntity(coordinator, mac, ip, entry.entry_id))
            
        if new_entities:
            async_add_entities(new_entities)

    # Ascolta gli aggiornamenti per trovare nuovi dispositivi
    coordinator.async_add_listener(add_new_entities)
    
    # Aggiungi i dispositivi iniziali
    add_new_entities()

    return True


class TendaScannerEntity(CoordinatorEntity, ScannerEntity):
    """Rappresenta un dispositivo tracciato sul Tenda i29."""

    def __init__(self, coordinator, mac_address, ip_address, entry_id):
        """Inizializza l'entità tracker."""
        super().__init__(coordinator)
        self._mac_address = mac_address
        self._ip_address = ip_address
        self._attr_unique_id = f"tenda_i29_{mac_address}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    @property
    def mac_address(self) -> str:
        """Ritorna l'indirizzo MAC del dispositivo."""
        return self._mac_address

    @property
    def ip_address(self) -> str:
        """Ritorna l'indirizzo IP del dispositivo."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._mac_address, self._ip_address)
        return self._ip_address

    @property
    def name(self) -> str:
        """Ritorna il nome del dispositivo basato sul MAC."""
        return f"Tenda {self._mac_address[-8:].upper()}"

    @property
    def is_connected(self) -> bool:
        """Ritorna True se il dispositivo è connesso."""
        if self.coordinator.data:
            return self._mac_address in self.coordinator.data
        return False

    @property
    def source_type(self) -> SourceType:
        """Ritorna il tipo di sorgente (Router)."""
        return SourceType.ROUTER
