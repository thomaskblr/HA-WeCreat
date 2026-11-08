"""Laser process status."""
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import DOMAIN
from .api import LABELS


async def async_setup_entry(hass, entry, async_add_entities):
    async_add_entities([ProcessStatus(entry)])


class ProcessStatus(CoordinatorEntity, SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "process_status"
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = [*LABELS.values(), "unrecognized"]

    def __init__(self, entry):
        super().__init__(entry.runtime_data)
        self._attr_unique_id = f"{entry.entry_id}_process_status"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)}, name=entry.title,
            manufacturer="WeCreat",
        )

    @property
    def native_value(self):
        return LABELS.get(self.coordinator.data, "unrecognized")

    @property
    def extra_state_attributes(self):
        return {"raw_status": self.coordinator.data}
