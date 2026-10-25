"""IR codes for Nordic Flame and L8 Design LED candle remotes.

NEC extended, address 0xB708, 38 kHz. Same set as
infrared_protocols' Generic10KeyB708Code; defined here so the integration
works regardless of which library version Home Assistant ships.
"""

from enum import IntEnum

from infrared_protocols.commands import Command
from infrared_protocols.commands.nec import NECCommand

NEC_ADDRESS = 0xB708


class NordicFlameCode(IntEnum):
    """Remote command codes."""

    ON = 0x00
    OFF = 0x02
    TIMER_2H = 0x04
    TIMER_4H = 0x06
    TIMER_6H = 0x08
    TIMER_8H = 0x0A
    CANDLE = 0x0C
    LIGHT = 0x0E
    BRIGHTNESS_DOWN = 0x10
    BRIGHTNESS_UP = 0x12

    def to_command(self, repeat_count: int = 0) -> Command:
        """Build the NEC command."""
        return NECCommand(
            address=NEC_ADDRESS, command=self.value, repeat_count=repeat_count
        )
