DOMAIN = "tesla_scheduler"

async def async_setup(hass, config):
    return True

async def async_setup_entry(hass, config_entry):
    hass.async_create_task(
        hass.config_entries.async_forward_entry_setup(config_entry, "sensor")
    )
    return True