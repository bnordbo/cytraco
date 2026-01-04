"""Trainer detection and BLE scanning. Alias: trn."""

from dataclasses import dataclass
from pathlib import Path

import bleak

from cytraco import bootstrap, errors
from cytraco.model import config as cfg

FTMS_SERVICE_UUID = "00001826-0000-1000-8000-00805f9b34fb"


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


async def scan_for_trainers() -> list[TrainerInfo]:
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


async def detect_trainer(config_handler: bootstrap.AppConfig, config_path: Path) -> TrainerInfo:
    """Detect and persist trainer selection.

    Scans for BLE trainers and handles selection. If exactly one trainer is
    found, saves it to config and returns it. Otherwise, raises an error.
    Preserves existing config values (like FTP) when updating device address.

    Args:
        config_handler: AppConfig implementation for persisting selection
        config_path: Path to configuration file

    Returns:
        TrainerInfo for the detected trainer

    Raises:
        DeviceError: If no trainers found or multiple trainers found
    """
    trainers = await scan_for_trainers()

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
