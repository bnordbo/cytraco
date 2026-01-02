"""Test data generators."""

# ruff: noqa: S311

import random

from cytraco.model.config import Config
from cytraco.model.power import PowerData
from cytraco.trainer import TrainerInfo


def mac_address() -> str:
    """Generate a random MAC address for testing."""
    return ":".join(f"{random.randint(0, 255):02X}" for _ in range(6))


def ftp() -> int:
    """Generate a random FTP value for testing."""
    return random.randint(150, 400)


def power_data() -> PowerData:
    """Generate random PowerData for testing."""
    return PowerData(power=random.randint(100, 400))


def trainer_info() -> TrainerInfo:
    """Generate random TrainerInfo for testing."""
    names = ["Tacx Neo 2T", "Wahoo KICKR", "Elite Direto", "Saris H3"]
    return TrainerInfo(
        name=random.choice(names), address=mac_address(), rssi=random.randint(-90, -30),
    )


def config() -> Config:
    """Generate random Config for testing."""
    return Config(
        device_address=mac_address(),
        ftp=ftp(),
    )
