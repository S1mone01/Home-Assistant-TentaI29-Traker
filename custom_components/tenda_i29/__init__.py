from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform

from .const import DOMAIN

PLATFORMS = [Platform.DEVICE_TRACKER]

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configura l'integrazione Tenda i29."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura il Tenda i29 da un Config Entry."""
    hass.data.setdefault(DOMAIN, {})
    # Salviamo i dati di configurazione nell'istanza di HA
    hass.data[DOMAIN][entry.entry_id] = entry.data

    # Invia la configurazione alla piattaforma device_tracker
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove l'integrazione correttamente se eliminata dalla UI."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
