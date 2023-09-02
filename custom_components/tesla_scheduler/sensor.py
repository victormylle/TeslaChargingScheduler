import requests
from homeassistant.helpers.entity import Entity
import logging

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.info("Setting up sensors...")

    ip_address = config_entry.data["ip_address"]
    endpoint = f"http://{ip_address}/your_endpoint"

    try:
        data = await hass.async_add_executor_job(lambda: requests.get(endpoint).json())
        _LOGGER.info(f"Retrieved data: {data}")
    except Exception as e:
        _LOGGER.error(f"Could not retrieve data: {e}")
        return

    sensors = []
    for key, value in data.items():
        sensors.append(MySensor(key, value))

    _LOGGER.info(f"Adding {len(sensors)} sensors.")
    async_add_entities(sensors, True)


class MySensor(Entity):
    def __init__(self, name, state):
        self._name = name
        self._state = state

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
