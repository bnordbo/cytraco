"""Tests for trainer."""

from unittest.mock import AsyncMock, MagicMock

import bleak
import pytest

from cytraco import errors
from cytraco.trainer import check_connection, scan_for_trainers
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


@pytest.mark.asyncio
async def test_check_connection_success(monkeypatch: pytest.MonkeyPatch) -> None:
    """check_connection should return True when connection succeeds."""
    address = generate.mac_address()

    # Mock BleakClient to succeed silently
    mock_client = AsyncMock()
    mock_client.__aenter__ = AsyncMock(return_value=mock_client)
    mock_client.__aexit__ = AsyncMock(return_value=None)
    monkeypatch.setattr("cytraco.trainer.bleak.BleakClient", lambda _: mock_client)

    result = await check_connection(address)

    assert result is True


@pytest.mark.asyncio
async def test_check_connection_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """check_connection should return False when connection fails."""
    address = generate.mac_address()

    # Mock BleakClient to raise exception
    class MockClient:
        async def __aenter__(self):  # noqa: ANN204
            raise bleak.BleakError("Connection failed")

        async def __aexit__(self, *_):  # noqa: ANN002, ANN204
            pass

    monkeypatch.setattr("cytraco.trainer.bleak.BleakClient", lambda _: MockClient())

    result = await check_connection(address)

    assert result is False
