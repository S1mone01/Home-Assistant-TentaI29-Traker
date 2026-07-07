import logging
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PASSWORD
from homeassistant.core import callback

from .const import DOMAIN
# Importiamo il client che abbiamo scritto prima per testare le credenziali al login
from .client import TendaI29Client 

_LOGGER = logging.getLogger(__name__)

class TendaI29ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Gestisce il config flow per Tenda i29."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Gestisce il primo step di configurazione dell'utente."""
        errors = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            password = user_input[CONF_PASSWORD]

            # Validazione delle credenziali (eseguita in un thread separato per non bloccare HA)
            client = TendaI29Client(host, password)
            try:
                await self.hass.async_add_executor_job(client.auth)
                if client.cookies is not None:
                    return self.async_create_entry(
                        title=f"Tenda i29 ({host})", 
                        data=user_input
                    )
                else:
                    errors["base"] = "invalid_auth"
            except Exception:
                errors["base"] = "cannot_connect"

        DATA_SCHEMA = vol.Schema(
            {
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )
