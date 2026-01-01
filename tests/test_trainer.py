"""Tests for trainer."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from cytraco.errors import DeviceError
from cytraco.trainer import scan_for_trainers


@pytest.mark.asyncio
async def test_scan_for_trainers_finds_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should find trainers with FTMS."""
    # Create mock device and advertisement data
    mock_device = MagicMock()
    mock_device.name = "Tacx Neo 2T"
    mock_device.address = "AA:BB:CC:DD:EE:FF"

    mock_adv = MagicMock()
    mock_adv.rssi = -65

    # Mock BleakScanner.discover to return dict with device tuple
    mock_discover = AsyncMock(
        return_value={"AA:BB:CC:DD:EE:FF": (mock_device, mock_adv)}
    )
    monkeypatch.setattr("cytraco.trainer.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 1
    assert trainers[0].name == "Tacx Neo 2T"
    assert trainers[0].address == "AA:BB:CC:DD:EE:FF"
    assert trainers[0].rssi == -65
    mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_scan_for_trainers_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should pass timeout parameter to discover."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.BleakScanner.discover", mock_discover)

    await scan_for_trainers(timeout=10.0)

    mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_scan_for_trainers_no_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should return empty list when no trainers found."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 0


@pytest.mark.asyncio
async def test_scan_for_trainers_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should raise DeviceConnectionError on BLE failure."""
    mock_discover = AsyncMock(side_effect=Exception("BLE error"))
    monkeypatch.setattr("cytraco.trainer.BleakScanner.discover", mock_discover)

    with pytest.raises(DeviceError) as exc_info:
        await scan_for_trainers()

    assert "BLE scan failed" in str(exc_info.value)


@pytest.mark.asyncio
async def test_scan_for_trainers_unknown_name(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should handle devices with no name."""
    mock_device = MagicMock()
    mock_device.name = None
    mock_device.address = "AA:BB:CC:DD:EE:FF"

    mock_adv = MagicMock()
    mock_adv.rssi = -70

    mock_discover = AsyncMock(
        return_value={"AA:BB:CC:DD:EE:FF": (mock_device, mock_adv)}
    )
    monkeypatch.setattr("cytraco.trainer.BleakScanner.discover", mock_discover)

    trainers = await scan_for_trainers()

    assert len(trainers) == 1
    assert trainers[0].name == "Unknown"
    assert trainers[0].rssi == -70
