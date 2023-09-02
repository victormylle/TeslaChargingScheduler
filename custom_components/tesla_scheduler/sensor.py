import requests
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import async_track_time_interval
import logging
import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.warning("Setting up sensors...")

    ip_address = config_entry.data["ip_address"]
    endpoint = f"http://{ip_address}/scheduled"

    try:
        data = await hass.async_add_executor_job(lambda: requests.get(endpoint).json())
        _LOGGER.warning(f"Retrieved data: {data}")
    except Exception as e:
        _LOGGER.error(f"Could not retrieve data: {e}")
        return

    sensors = []
    for key, value in data.items():
        sensors.append(MySensor(key, value, hass, endpoint))

    _LOGGER.warning(f"Adding {len(sensors)} sensors.")
    async_add_entities(sensors, True)

class MySensor(Entity):
    def __init__(self, name, state, hass, endpoint):
        self._name = name
        self._state = state
        self._hass = hass
        self._endpoint = endpoint

        # Update every minute
        async_track_time_interval(self._hass, self.async_update, datetime.timedelta(minutes=1))

    @property
    def name(self):
        return f"tesla_scheduler_{self._name}"

    @property
    def state(self):
        return self._state
    
    @property
    def unique_id(self):
        return f"tesla_scheduler_{self._name}"


    async def async_update(self, *args):
        try:
            self._state = await self._hass.async_add_executor_job(lambda: requests.get(self._endpoint).json()[self._name])
            _LOGGER.warning(f"Updated sensor {self._name} to {self._state}")
        except Exception as e:
            _LOGGER.error(f"Could not update sensor {self._name}: {e}")
