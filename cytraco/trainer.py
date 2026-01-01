"""Trainer detection and BLE scanning."""

import sys
from dataclasses import dataclass

import bleak

from cytraco import errors


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


async def scan_for_trainers(timeout: float = 5.0) -> list[TrainerInfo]:
    """Scan for BLE trainers with FTMS.

    Args:
        timeout: Scan duration in seconds

    Returns:
        List of discovered trainers with FTMS

    Raises:
        DeviceError: If BLE scanning fails
    """
    try:
        devices = await bleak.BleakScanner.discover(
            timeout=timeout,
            service_uuids=[FTMS_SERVICE_UUID],
            return_adv=True,
        )
    except Exception as e:
        raise errors.DeviceError(f"BLE scan failed: {e}") from e

    return [
        TrainerInfo(name=d.name or "Unknown", address=d.address, rssi=adv.rssi)
        for d, adv in devices.values()
    ]


async def detect_trainer() -> None:
    """Detect and report available trainers.

    Scans for BLE trainers and reports the result. If exactly one trainer is
    found, prints the trainer name and exits successfully. Otherwise, exits with
    an error.

    Raises:
        SystemExit: Always (with code 0 on success, 1 on error)
    """
    trainers = await scan_for_trainers()

    if len(trainers) == 0:
        print("Error: No trainers found")
        sys.exit(1)
    elif len(trainers) > 1:
        print(f"Error: Found {len(trainers)} trainers, expected exactly 1")
        sys.exit(1)
    else:
        print(f"Found trainer: {trainers[0].name}")
        sys.exit(0)
