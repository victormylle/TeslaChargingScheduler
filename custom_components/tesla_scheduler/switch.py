import requests
from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.event import async_track_time_interval
import logging
import datetime

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    _LOGGER.warning("Setting up switches...")

    ip_address = config_entry.data["ip_address"]
    endpoint_get = f"http://{ip_address}/scheduled"
    endpoint_post = f"http://{ip_address}/charge_tonight"

    try:
        data = await hass.async_add_executor_job(lambda: requests.get(endpoint_get).json())
        _LOGGER.warning(f"Retrieved data: {data}")
    except Exception as e:
        _LOGGER.error(f"Could not retrieve data: {e}")
        return

    switches = []
    for key, value in data.items():
        switches.append(MySwitch(key, value, hass, endpoint_get, endpoint_post))

    _LOGGER.warning(f"Adding {len(switches)} switches.")
    async_add_entities(switches, True)

class MySwitch(SwitchEntity):
    def __init__(self, name, state, hass, endpoint_get, endpoint_post):
        self._name = name
        self._is_on = state
        self._hass = hass
        self._endpoint_get = endpoint_get
        self._endpoint_post = endpoint_post

        async_track_time_interval(self._hass, self.async_update, datetime.timedelta(minutes=1))

    @property
    def name(self):
        return f"tesla_scheduler_{self._name}"

    @property
    def is_on(self):
        return self._is_on

    @property
    def unique_id(self):
        return f"tesla_scheduler_{self._name}"

    async def async_turn_on(self, **kwargs):
        try:
            await self._hass.async_add_executor_job(lambda: requests.post(self._endpoint_post, json={"state": "on"}))
            self._is_on = True
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Could not turn on the switch: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            await self._hass.async_add_executor_job(lambda: requests.post(self._endpoint_post, json={"state": "off"}))
            self._is_on = False
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Could not turn off the switch: {e}")

    async def async_update(self, *args):
        try:
            self._is_on = await self._hass.async_add_executor_job(lambda: requests.get(self._endpoint_get).json()[self._name])
            _LOGGER.warning(f"Updated switch {self._name} to {self._is_on}")
        except Exception as e:
            _LOGGER.error(f"Could not update switch {self._name}: {e}")
