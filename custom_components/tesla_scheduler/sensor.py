from homeassistant.helpers.entity import Entity
import requests

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip_address = config_entry.data["ip_address"]
    endpoint = f"http://{ip_address}/your_endpoint"

    # Fetch data asynchronously using the executor
    data = await hass.async_add_executor_job(lambda: requests.get(endpoint).json())

    sensors = []
    for key, value in data.items():
        sensors.append(MySensor(key, value))
    # ... Repeat for other fields in your JSON

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
