"""Trainer detection and BLE scanning. Alias: trn."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

import bleak

import cytraco.model.config as cfg
from cytraco import errors


class ConfigHandler(Protocol):
    """Protocol for config persistence in detect_trainer."""

    def load_file(self, path: Path) -> cfg.Config:
        """Load config from path."""
        ...

    def write_file(self, path: Path, config: cfg.Config) -> None:
        """Write config to path."""
        ...

FTMS_SERVICE_UUID = "00001826-0000-1000-8000-00805f9b34fb"


class UserAction(Enum):
    """Actions user can take during trainer selection."""

    RETRY = "retry"
    SCAN = "scan"
    EXIT = "exit"
    DEMO = "demo"


@dataclass
class TrainerInfo:
    """Information about a discovered trainer.

    Attributes:
        name: Human-readable device name
        address: BLE device address
        rssi: Signal strength in dBm
    """

    name: str
    address: str
    rssi: int


@dataclass
class TrainerSelected:
    """Result when user selects a trainer."""

    trainer: TrainerInfo


TrainerResult = TrainerSelected | UserAction


class BleakTrainerScanner:
    """Trainer scanner implementation using Bleak BLE library."""

    async def scan(self) -> list[TrainerInfo]:
        """Scan for BLE trainers with FTMS.

        Scans for 10 seconds. Callers needing different timeout behavior
        should wrap with asyncio.timeout().

        Returns:
            List of discovered trainers with FTMS

        Raises:
            DeviceError: If BLE scanning fails
        """
        try:
            devices = await bleak.BleakScanner.discover(
                timeout=10.0,
                service_uuids=[FTMS_SERVICE_UUID],
                return_adv=True,
            )
        except Exception as e:
            raise errors.DeviceError(f"BLE scan failed: {e}") from e

        return [
            TrainerInfo(name=d.name or "Unknown", address=d.address, rssi=adv.rssi)
            for d, adv in devices.values()
        ]

    async def connect(self, address: str) -> bool:
        """Connect to a trainer at the given BLE address.

        Args:
            address: BLE address of the trainer.

        Returns:
            True if connection successful, False otherwise.
        """
        try:
            async with bleak.BleakClient(address) as client:
                return client.is_connected
        except (bleak.exc.BleakError, OSError, TimeoutError):
            return False


async def detect_trainer(config_handler: ConfigHandler, config_path: Path) -> TrainerInfo:
    """Detect and persist trainer selection.

    Scans for BLE trainers and handles selection. If exactly one trainer is
    found, saves it to config and returns it. Otherwise, raises an error.
    Preserves existing config values (like FTP) when updating device address.

    Args:
        config_handler: ConfigHandler implementation for persisting selection
        config_path: Path to configuration file

    Returns:
        TrainerInfo for the detected trainer

    Raises:
        DeviceError: If no trainers found or multiple trainers found
    """
    trainers = await BleakTrainerScanner().scan()

    if len(trainers) == 0:
        raise errors.DeviceError("No trainers found")
    if len(trainers) > 1:
        raise errors.DeviceError(f"Found {len(trainers)} trainers, expected exactly 1")

    # Load existing config or create new one
    try:
        config = config_handler.load_file(config_path)
    except FileNotFoundError:
        config = cfg.Config(ftp=300)

    # Update device address and save
    trainer = trainers[0]
    config.device_address = trainer.address
    config_handler.write_file(config_path, config)

    return trainer
