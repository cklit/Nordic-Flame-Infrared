"""Button platform for Nordic Flame."""

from typing import override

from homeassistant.components.button import ButtonEntity
from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import NordicFlameCode
from .const import CONF_INFRARED_ENTITY_ID
from .entity import NordicFlameBaseEntity

PARALLEL_UPDATES = 1

BUTTONS = [
    NordicFlameCode.BRIGHTNESS_UP,
    NordicFlameCode.BRIGHTNESS_DOWN,
    NordicFlameCode.TIMER_2H,
    NordicFlameCode.TIMER_4H,
    NordicFlameCode.TIMER_6H,
    NordicFlameCode.TIMER_8H,
    NordicFlameCode.CANDLE,
    NordicFlameCode.LIGHT,
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up buttons from a config entry."""
    if not (infrared_entity_id := entry.data.get(CONF_INFRARED_ENTITY_ID)):
        return

    async_add_entities(
        NordicFlameButtonEntity(entry, infrared_entity_id, code) for code in BUTTONS
    )


class NordicFlameButtonEntity(
    NordicFlameBaseEntity, InfraredEmitterConsumerEntity, ButtonEntity
):
    """Button that sends one IR code."""

    def __init__(
        self, entry: ConfigEntry, infrared_entity_id: str, code: NordicFlameCode
    ) -> None:
        """Initialize the entity."""
        super().__init__(entry)
        self._infrared_emitter_entity_id = infrared_entity_id
        self._code = code
        key = code.name.lower()
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_translation_key = key

    @override
    async def async_press(self) -> None:
        """Press the button."""
        await self._send_command(self._code.to_command())
