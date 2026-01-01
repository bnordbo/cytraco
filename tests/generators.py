"""Test data generators."""

import random

from cytraco.model.power import PowerData


def mac_address() -> str:
    """Generate a random MAC address for testing."""
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))


def ftp() -> int:
    """Generate a random FTP value for testing."""
    return random.randint(150, 400)


def power_data() -> PowerData:
    """Generate random PowerData for testing."""
    return PowerData(power=random.randint(100, 400))
