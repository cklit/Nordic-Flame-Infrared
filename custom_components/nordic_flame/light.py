"""Light platform for Nordic Flame."""

from typing import Any, override

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.components.light import (
    ATTR_EFFECT,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import NordicFlameCode
from .const import CONF_INFRARED_ENTITY_ID
from .entity import NordicFlameBaseEntity

PARALLEL_UPDATES = 1

EFFECTS = ["candle", "light"]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the light from a config entry."""
    if not (infrared_entity_id := entry.data.get(CONF_INFRARED_ENTITY_ID)):
        return

    async_add_entities([NordicFlameLightEntity(entry, infrared_entity_id)])


class NordicFlameLightEntity(
    NordicFlameBaseEntity, InfraredEmitterConsumerEntity, LightEntity
):
    """Candle light. State is assumed, since IR is one-way."""

    _attr_assumed_state = True
    _attr_color_mode = ColorMode.ONOFF
    _attr_supported_color_modes = {ColorMode.ONOFF}
    _attr_supported_features = LightEntityFeature.EFFECT
    _attr_effect_list = EFFECTS
    _attr_name = None
    _attr_translation_key = "light"

    def __init__(self, entry: ConfigEntry, infrared_entity_id: str) -> None:
        """Initialize the entity."""
        super().__init__(entry)
        self._infrared_emitter_entity_id = infrared_entity_id
        self._attr_unique_id = entry.entry_id

    @override
    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on, optionally setting an effect."""
        await self._send_command(NordicFlameCode.ON.to_command())
        self._attr_is_on = True
        effect: str | None = kwargs.get(ATTR_EFFECT)
        if effect in EFFECTS:
            await self._send_command(NordicFlameCode[effect.upper()].to_command())
            self._attr_effect = effect
        self.async_write_ha_state()

    @override
    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off."""
        await self._send_command(NordicFlameCode.OFF.to_command())
        self._attr_is_on = False
        self.async_write_ha_state()

    @callback
    def _async_handle_event(self, event_type: str) -> None:
        """Update assumed state from a key press seen by the receiver."""
        if event_type in ("on", "off"):
            self._attr_is_on = event_type == "on"
        elif event_type in EFFECTS:
            self._attr_is_on = True
            self._attr_effect = event_type
        else:
            return
        self.async_write_ha_state()

    @override
    async def async_added_to_hass(self) -> None:
        """Listen for key presses from the event entity."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._entry.entry_id, self._async_handle_event
            )
        )
        await super().async_added_to_hass()
