import aiohttp
from datetime import timedelta
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.entity import Entity

async def async_setup_entry(hass, config_entry, async_add_entities):
    ip_address = config_entry.data["ip_address"]
    endpoint = f"http://{ip_address}/your_endpoint"

    # Initialize entities list
    entities = []

    async def fetch_data():
        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint) as response:
                data = await response.json()
        # Your logic to update entities
        for entity in entities:
            entity.update_data(data[entity.name])
            
    # Register the fetch data method to be called every 15 seconds
    async_track_time_interval(hass, fetch_data, timedelta(seconds=15))

    # Create initial entities based on first data fetch
    await fetch_data()

    # Actually add the entities
    async_add_entities(entities, True)

class MySensor(Entity):
    def __init__(self, name):
        self._name = name
        self._state = None

    def update_data(self, new_state):
        self._state = new_state
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        return self._name

    @property
    def state(self):
        return self._state
