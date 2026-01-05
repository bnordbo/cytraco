"""Trainer detection and BLE scanning. Alias: trn."""

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


async def check_connection(address: str) -> bool:
    """Test BLE connection to trainer at given address.

    Attempts to establish a BLE connection to verify the trainer is reachable.
    Does not raise exceptions on connection failure.

    Args:
        address: BLE device address to test

    Returns:
        True if connection successful, False otherwise
    """
    try:
        async with bleak.BleakClient(address):
            return True
    except (bleak.BleakError, OSError, TimeoutError):
        return False
