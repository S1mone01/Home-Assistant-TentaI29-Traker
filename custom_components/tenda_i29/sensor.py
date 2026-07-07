import logging
from datetime import datetime, timezone
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Configura la piattaforma sensor."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]

    sensors = [
        TendaConnectedDevicesSensor(coordinator, entry.entry_id),
        TendaLastCheckedSensor(coordinator, entry.entry_id)
    ]
    
    async_add_entities(sensors)
    return True

class TendaConnectedDevicesSensor(CoordinatorEntity, SensorEntity):
    """Sensore che mostra il totale dei dispositivi connessi."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_name = "Tenda i29 Dispositivi Connessi"
        self._attr_unique_id = f"tenda_i29_connected_devices_{entry_id}"
        self._attr_icon = "mdi:devices"
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "dispositivi"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    @property
    def native_value(self):
        """Ritorna il numero di dispositivi connessi."""
        if self.coordinator.data:
            return len(self.coordinator.data)
        return 0

class TendaLastCheckedSensor(CoordinatorEntity, SensorEntity):
    """Sensore che mostra l'orario dell'ultimo controllo riuscito."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_name = "Tenda i29 Ultimo Controllo"
        self._attr_unique_id = f"tenda_i29_last_checked_{entry_id}"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP
        self._attr_icon = "mdi:clock-check-outline"
        self._last_updated = None
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    @property
    def native_value(self):
        """Ritorna il timestamp dell'ultimo aggiornamento riuscito."""
        if self.coordinator.last_update_success:
            self._last_updated = datetime.now(timezone.utc)
        return self._last_updated
