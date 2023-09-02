import voluptuous as vol
from homeassistant import config_entries

DOMAIN = "tesla_scheduler"

class MyCustomComponentConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}
        
        if user_input is not None:
            return self.async_create_entry(
                title="My Custom Component",
                data={"ip_address": user_input["ip_address"]},
            )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("ip_address"): str,
            }),
            errors=errors,
        )
