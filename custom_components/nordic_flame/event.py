"""Event platform for Nordic Flame: fires when the physical remote is used."""

import logging
from typing import override

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.event import EventEntity
from homeassistant.components.infrared import (
    InfraredReceivedSignal,
    InfraredReceiverConsumerEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .codes import NEC_ADDRESS, NordicFlameCode
from .const import CONF_INFRARED_RECEIVER_ENTITY_ID
from .entity import NordicFlameBaseEntity

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the event entity from a config entry."""
    if not (receiver_entity_id := entry.data.get(CONF_INFRARED_RECEIVER_ENTITY_ID)):
        return

    async_add_entities([NordicFlameEventEntity(entry, receiver_entity_id)])


class NordicFlameEventEntity(
    NordicFlameBaseEntity, InfraredReceiverConsumerEntity, EventEntity
):
    """Fires an event for each key press received."""

    _attr_translation_key = "received_command"
    _attr_event_types = [code.name.lower() for code in NordicFlameCode]

    def __init__(self, entry: ConfigEntry, receiver_entity_id: str) -> None:
        """Initialize the event entity."""
        super().__init__(entry)
        self._attr_unique_id = entry.entry_id
        self._infrared_receiver_entity_id = receiver_entity_id

    @callback
    @override
    def _handle_signal(self, signal: InfraredReceivedSignal) -> None:
        """Handle a received IR signal."""
        received = NECCommand.from_raw_timings(signal.timings)
        if received is None or received.address != NEC_ADDRESS:
            return

        try:
            code = NordicFlameCode(received.command)
        except ValueError:
            return

        event_type = code.name.lower()
        _LOGGER.debug("Received command: %s (0x%02X)", event_type, code.value)

        self._trigger_event(event_type)
        async_dispatcher_send(self.hass, self._entry.entry_id, event_type)
        self.async_write_ha_state()
