import logging
from datetime import timedelta

from homeassistant.components.device_tracker.config_entry import ScannerEntity, SourceType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity
from homeassistant.helpers import device_registry as dr
from homeassistant.const import CONF_HOST, CONF_PASSWORD

from .const import DOMAIN
from .client import TendaI29Client

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configura la piattaforma device_tracker basata sul Config Flow."""
    config = hass.data[DOMAIN][entry.entry_id]
    host = config[CONF_HOST]
    password = config[CONF_PASSWORD]
    
    client = TendaI29Client(host, password)
    
    async def async_update_data():
        """Recupera i dati dai client connessi dal router."""
        return await hass.async_add_executor_job(client.get_connected_devices)
        
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Tenda i29 ({host})",
        update_method=async_update_data,
        update_interval=timedelta(seconds=30),
    )

    # Recupera i dati iniziali
    await coordinator.async_config_entry_first_refresh()

    tracked_macs = set()

    @callback
    def add_new_entities():
        """Aggiunge nuove entità in base ai MAC rilevati."""
        new_entities = []
        if coordinator.data:
            for mac, ip in coordinator.data.items():
                if mac not in tracked_macs:
                    tracked_macs.add(mac)
                    new_entities.append(TendaScannerEntity(coordinator, mac, ip))
            
        if new_entities:
            async_add_entities(new_entities)

    # Ascolta gli aggiornamenti per trovare nuovi dispositivi
    coordinator.async_add_listener(add_new_entities)
    
    # Aggiungi i dispositivi iniziali
    add_new_entities()

    return True


class TendaScannerEntity(CoordinatorEntity, ScannerEntity):
    """Rappresenta un dispositivo tracciato sul Tenda i29."""

    def __init__(self, coordinator, mac_address, ip_address):
        """Inizializza l'entità tracker."""
        super().__init__(coordinator)
        self._mac_address = mac_address
        self._ip_address = ip_address
        self._attr_unique_id = f"tenda_i29_{mac_address}"

    @property
    def mac_address(self) -> str:
        """Ritorna l'indirizzo MAC del dispositivo."""
        return self._mac_address

    @property
    def ip_address(self) -> str:
        """Ritorna l'indirizzo IP del dispositivo."""
        # Aggiorna l'IP se è cambiato
        if self.coordinator.data:
            return self.coordinator.data.get(self._mac_address, self._ip_address)
        return self._ip_address

    @property
    def name(self) -> str:
        """Ritorna il nome del dispositivo. L'i29 fornisce l'IP come identificativo."""
        return self.ip_address

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
