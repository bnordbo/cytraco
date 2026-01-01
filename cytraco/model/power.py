"""Power measurement model for Cytraco."""

from dataclasses import dataclass


@dataclass
class PowerData:
    """Power measurement data.

    Attributes:
        power: Instantaneous power in watts.
    """

    power: int
