"""Tests for trainer."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cytraco import errors
from cytraco.trainer import scan_for_trainers
from tests import generators as generate


@pytest.mark.asyncio
async def test_scan_for_trainers_finds_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should find trainers with FTMS."""
    # Create mock device and advertisement data
    trainer = generate.trainer_info()
    mock_device = MagicMock()
    mock_device.name = trainer.name
    mock_device.address = trainer.address

    mock_adv = MagicMock()
    mock_adv.rssi = trainer.rssi

    # Mock BleakScanner.discover to return dict with device tuple
    mock_discover = AsyncMock(
        return_value={trainer.address: (mock_device, mock_adv)},
    )
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 1
    assert trainers[0].name == trainer.name
    assert trainers[0].address == trainer.address
    assert trainers[0].rssi == trainer.rssi
    mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_scan_for_trainers_calls_discover(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should call BleakScanner.discover."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    await scan_for_trainers()

    mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_scan_for_trainers_no_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should return empty list when no trainers found."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 0


@pytest.mark.asyncio
async def test_scan_for_trainers_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should raise DeviceConnectionError on BLE failure."""
    mock_discover = AsyncMock(side_effect=Exception("BLE error"))
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    with pytest.raises(errors.DeviceError) as exc_info:
        await scan_for_trainers()

    assert "BLE scan failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scan_for_trainers_unknown_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should handle devices with no name."""
    trainer = generate.trainer_info()
    mock_device = MagicMock()
    mock_device.name = None
    mock_device.address = trainer.address

    mock_adv = MagicMock()
    mock_adv.rssi = trainer.rssi

    mock_discover = AsyncMock(
        return_value={trainer.address: (mock_device, mock_adv)},
    )
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 1
    assert trainers[0].name == "Unknown"
    assert trainers[0].rssi == trainer.rssi
