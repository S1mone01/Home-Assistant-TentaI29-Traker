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
        TendaDeviceList24GSensor(coordinator, entry.entry_id),
        TendaDeviceList5GSensor(coordinator, entry.entry_id),
        TendaLastCheckedSensor(coordinator, entry.entry_id),
    ]
    
    async_add_entities(sensors)
    return True

class TendaDeviceList24GSensor(CoordinatorEntity, SensorEntity):
    """Sensore che mostra l'elenco dei dispositivi connessi a 2.4GHz."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_name = "Tenda i29 Dispositivi 2.4GHz"
        self._attr_unique_id = f"tenda_i29_device_list_24g_{entry_id}"
        self._attr_icon = "mdi:wifi"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    @property
    def native_value(self):
        """Ritorna il numero di dispositivi a 2.4GHz come stato."""
        if self.coordinator.data:
            count = sum(1 for d in self.coordinator.data.values() if d.get("band") == "2.4GHz")
            return f"{count} connessi"
        return "0 connessi"

    @property
    def extra_state_attributes(self):
        """Ritorna l'elenco completo dei dispositivi a 2.4GHz come attributi."""
        if not self.coordinator.data:
            return {"dispositivi": []}

        device_list = []
        for mac, info in self.coordinator.data.items():
            if info.get("band") == "2.4GHz":
                device_list.append({
                    "mac": mac.upper(),
                    "ip": info.get("ip", ""),
                    "connesso_da": info.get("connect_time", ""),
                    "velocita_tx": f"{info.get('tx_rate', '0')} Mbps",
                    "velocita_rx": f"{info.get('rx_rate', '0')} Mbps",
                    "segnale": info.get("signal", ""),
                })

        device_list.sort(key=lambda d: tuple(int(p) for p in d["ip"].split(".")) if d["ip"] else (999,))
        return {"dispositivi": device_list}

class TendaDeviceList5GSensor(CoordinatorEntity, SensorEntity):
    """Sensore che mostra l'elenco dei dispositivi connessi a 5GHz."""

    def __init__(self, coordinator, entry_id):
        super().__init__(coordinator)
        self._attr_name = "Tenda i29 Dispositivi 5GHz"
        self._attr_unique_id = f"tenda_i29_device_list_5g_{entry_id}"
        self._attr_icon = "mdi:wifi-strength-4"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry_id)},
            "name": "Tenda i29 Router",
            "manufacturer": "Tenda",
            "model": "i29",
        }

    @property
    def native_value(self):
        """Ritorna il numero di dispositivi a 5GHz come stato."""
        if self.coordinator.data:
            count = sum(1 for d in self.coordinator.data.values() if d.get("band") == "5GHz")
            return f"{count} connessi"
        return "0 connessi"

    @property
    def extra_state_attributes(self):
        """Ritorna l'elenco completo dei dispositivi a 5GHz come attributi."""
        if not self.coordinator.data:
            return {"dispositivi": []}

        device_list = []
        for mac, info in self.coordinator.data.items():
            if info.get("band") == "5GHz":
                device_list.append({
                    "mac": mac.upper(),
                    "ip": info.get("ip", ""),
                    "connesso_da": info.get("connect_time", ""),
                    "velocita_tx": f"{info.get('tx_rate', '0')} Mbps",
                    "velocita_rx": f"{info.get('rx_rate', '0')} Mbps",
                    "segnale": info.get("signal", ""),
                })

        device_list.sort(key=lambda d: tuple(int(p) for p in d["ip"].split(".")) if d["ip"] else (999,))
        return {"dispositivi": device_list}

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
