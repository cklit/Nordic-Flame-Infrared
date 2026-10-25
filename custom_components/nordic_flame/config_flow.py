"""Config flow for Nordic Flame."""

from typing import Any, override

import probatio

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
    async_get_receivers,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import EntitySelector, EntitySelectorConfig

from .const import CONF_INFRARED_ENTITY_ID, CONF_INFRARED_RECEIVER_ENTITY_ID, DOMAIN


class NordicFlameConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Nordic Flame."""

    VERSION = 1

    def _schema(self) -> probatio.Schema:
        return probatio.Schema(
            {
                probatio.Optional(CONF_INFRARED_ENTITY_ID): EntitySelector(
                    EntitySelectorConfig(
                        domain=INFRARED_DOMAIN,
                        include_entities=async_get_emitters(self.hass),
                    )
                ),
                probatio.Optional(CONF_INFRARED_RECEIVER_ENTITY_ID): EntitySelector(
                    EntitySelectorConfig(
                        domain=INFRARED_DOMAIN,
                        include_entities=async_get_receivers(self.hass),
                    )
                ),
            }
        )

    def _abort_if_used(self, user_input: dict[str, Any]) -> None:
        for key in (CONF_INFRARED_ENTITY_ID, CONF_INFRARED_RECEIVER_ENTITY_ID):
            if value := user_input.get(key):
                self._async_abort_entries_match({key: value})

    @override
    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if not async_get_emitters(self.hass) and not async_get_receivers(self.hass):
            return self.async_abort(reason="no_infrared_entities")

        errors: dict[str, str] = {}
        if user_input is not None:
            entity_id = user_input.get(CONF_INFRARED_ENTITY_ID) or user_input.get(
                CONF_INFRARED_RECEIVER_ENTITY_ID
            )
            if entity_id:
                self._abort_if_used(user_input)
                reg_entry = er.async_get(self.hass).async_get(entity_id)
                name = (
                    (reg_entry.name or reg_entry.original_name or entity_id)
                    if reg_entry
                    else entity_id
                )
                return self.async_create_entry(
                    title=f"Nordic Flame candle via {name}", data=user_input
                )
            errors["base"] = "missing_infrared_entity"

        return self.async_show_form(
            step_id="user", data_schema=self._schema(), errors=errors
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Change the emitter or receiver."""
        entry = self._get_reconfigure_entry()
        if not async_get_emitters(self.hass) and not async_get_receivers(self.hass):
            return self.async_abort(reason="no_infrared_entities")

        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get(CONF_INFRARED_ENTITY_ID) or user_input.get(
                CONF_INFRARED_RECEIVER_ENTITY_ID
            ):
                return self.async_update_reload_and_abort(entry, data=user_input)
            errors["base"] = "missing_infrared_entity"

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                self._schema(), entry.data
            ),
            errors=errors,
        )
