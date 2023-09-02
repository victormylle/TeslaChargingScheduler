from datetime import timedelta
import logging
import requests

from homeassistant.components.switch import SwitchEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.typing import ConfigType, HomeAssistantType
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistantType, config_entry: ConfigType, async_add_entities: AddEntitiesCallback):
    ip_address = config_entry.data["ip_address"]
    endpoint_get = f"http://{ip_address}/scheduled"
    endpoint_post = f"http://{ip_address}/charge_tonight"

    async def async_update_data():
        try:
            data = await hass.async_add_executor_job(lambda: requests.get(endpoint_get).json())
            return data["charge_tonight"]
        except Exception as err:
            raise UpdateFailed(f"Update failed: {err}")

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="charge_tonight",
        update_method=async_update_data,
        update_interval=timedelta(seconds=15),
    )

    await coordinator.async_config_entry_first_refresh()

    async_add_entities([MySwitch(coordinator, endpoint_post)], True)

class MySwitch(CoordinatorEntity, SwitchEntity):
    def __init__(self, coordinator: DataUpdateCoordinator, endpoint_post: str):
        super().__init__(coordinator)
        self._is_on = False
        self._endpoint_post = endpoint_post

    @property
    def is_on(self):
        return self._is_on

    async def async_turn_on(self, **kwargs):
        try:
            await self.hass.async_add_executor_job(lambda: requests.post(self._endpoint_post, json={"state": "on"}))
            self._is_on = True
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Could not turn on the switch: {e}")

    async def async_turn_off(self, **kwargs):
        try:
            await self.hass.async_add_executor_job(lambda: requests.post(self._endpoint_post, json={"state": "off"}))
            self._is_on = False
            self.async_write_ha_state()
        except Exception as e:
            _LOGGER.error(f"Could not turn off the switch: {e}")

    async def async_update(self):
        await super().async_update()
        self._is_on = self.coordinator.data.get("is_on", False)
