"""Trainer detection and BLE scanning. Alias: trn."""

# ruff: noqa: S311

import asyncio
import contextlib
import random
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

import bleak

import cytraco.model.config as cfg
from cytraco import errors
from cytraco.model.power import PowerData


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


class DemoPowerMeter:
    """Demo power meter producing synthetic power data.

    Simulates realistic power output with variations and drift. Useful for
    testing and development when no physical trainer is available.
    """

    def __init__(self, base_power: int = 200, update_interval: float = 1.0) -> None:
        """Initialize demo power meter.

        Args:
            base_power: Base power output in watts (default 200W)
            update_interval: Time between power updates in seconds (default 1.0s)
        """
        self._base_power = base_power
        self._update_interval = update_interval
        self._queue: asyncio.Queue[PowerData] = asyncio.Queue()
        self._task: asyncio.Task[None] | None = None
        self._running = False

    async def start(self) -> None:
        """Start generating synthetic power data.

        Begins continuous generation of PowerData objects with realistic
        variations around base_power. Data is placed on the queue at
        update_interval frequency.
        """
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._generate_power())

    async def stop(self) -> None:
        """Stop generating power data.

        Stops the generation task. The queue remains accessible for
        reading any remaining data.
        """
        self._running = False
        if self._task:
            self._task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._task
            self._task = None

    @property
    def queue(self) -> asyncio.Queue[PowerData]:
        """Queue containing generated power measurements.

        Returns:
            Queue that receives synthetic PowerData objects.
        """
        return self._queue

    async def _generate_power(self) -> None:
        """Generate synthetic power data continuously.

        Produces power values that vary realistically around base_power
        with random fluctuations (±15W) and slight drift over time.
        """
        drift = 0.0
        while self._running:
            # Add random variation and slow drift
            variation = random.randint(-15, 15)
            drift += random.uniform(-2, 2)
            drift = max(-30, min(30, drift))  # Limit drift to ±30W

            power = max(0, int(self._base_power + variation + drift))
            await self._queue.put(PowerData(power=power))
            await asyncio.sleep(self._update_interval)
