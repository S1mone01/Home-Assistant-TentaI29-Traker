from datetime import timedelta
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.const import Platform, CONF_HOST, CONF_PASSWORD
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .client import TendaI29Client

PLATFORMS = [Platform.DEVICE_TRACKER, Platform.SENSOR]

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Configura l'integrazione Tenda i29."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Configura il Tenda i29 da un Config Entry."""
    hass.data.setdefault(DOMAIN, {})
    
    host = entry.data[CONF_HOST]
    password = entry.data[CONF_PASSWORD]
    
    client = TendaI29Client(host, password)
    
    async def async_update_data():
        """Recupera i dati dai client connessi dal router."""
        devices = await hass.async_add_executor_job(client.get_connected_devices)
        
        # Se restituisce 0 dispositivi, probabile problema di sessione o riavvio router
        if not devices:
            # Azzera i cookie per forzare un nuovo login al prossimo tentativo
            client.cookies = None
            
            # Se avevamo già dei dati in precedenza (non è il primo avvio),
            # manteniamo i vecchi dati e ricarichiamo l'integrazione per sbloccarla.
            if getattr(coordinator, "data", None) is not None:
                _LOGGER.warning("Rilevati 0 dispositivi connessi. Mantengo i dati precedenti e ricarico l'integrazione.")
                hass.async_create_task(hass.config_entries.async_reload(entry.entry_id))
                return coordinator.data
            else:
                _LOGGER.warning("Rilevati 0 dispositivi connessi. Attendo il prossimo aggiornamento.")
                
        return devices
        
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"Tenda i29 ({host})",
        update_method=async_update_data,
        update_interval=timedelta(seconds=60),
    )

    # Recupera i dati iniziali (non bloccare il setup se fallisce)
    await coordinator.async_refresh()

    # Salviamo i dati nell'istanza di HA
    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "client": client
    }

    # Invia la configurazione alle piattaforme
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Rimuove l'integrazione correttamente se eliminata dalla UI."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
