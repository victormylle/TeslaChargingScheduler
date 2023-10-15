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

    periods = ["today", "yesterday", "month", "year"]
    for period in periods:
        sensor_name = f"charging_cost_{period}"
        sensors.append(ChargingCostSensor(sensor_name, hass, ip_address, period))


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

class ChargingCostSensor(Entity):
    def __init__(self, name, hass, ip_address, period):
        self._name = name
        self._state = 0.0  # Default state
        self._hass = hass
        self._period = period
        self._endpoint = f"http://{ip_address}/charging_cost?date={period}"

        # Update every minute
        async_track_time_interval(self._hass, self.async_update, datetime.timedelta(minutes=1))

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def unique_id(self):
        return self._name

    async def async_update(self, *args):
        try:
            start_date, end_date = self._get_date_range()
            endpoint = f"{self._base_endpoint}?start_date={start_date}&end_date={end_date}"
            response = await self._hass.async_add_executor_job(lambda: requests.get(endpoint).json())
            self._state = response.get("total_cost", 0.0)
            _LOGGER.warning(f"Updated sensor {self._name} to {self._state}")
        except Exception as e:
            _LOGGER.error(f"Could not update sensor {self._name}: {e}")

    def _get_date_range(self):
        today = datetime.date.today()
        if self._period == "today":
            return today, today
        elif self._period == "yesterday"":
            yesterday = today - datetime.timedelta(days=1)
            return yesterday, yesterday
        elif self._period == "month"":
            start_date = today.replace(day=1)
            end_date = today
            return start_date, end_date
        elif self._period == "year":
            start_date = today.replace(month=1, day=1)
            end_date = today
            return start_date, end_date