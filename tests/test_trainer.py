"""Tests for trainer."""

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

import pytest

import cytraco.trainer as trn
from cytraco import errors
from cytraco.model import config as cfg
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

    scanner = trn.BleakTrainerScanner()
    trainers = await scanner.scan()

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

    scanner = trn.BleakTrainerScanner()
    await scanner.scan()

    mock_discover.assert_called_once()


@pytest.mark.asyncio
async def test_scan_for_trainers_no_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should return empty list when no trainers found."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    scanner = trn.BleakTrainerScanner()
    trainers = await scanner.scan()

    assert len(trainers) == 0


@pytest.mark.asyncio
async def test_scan_for_trainers_error_handling(monkeypatch: pytest.MonkeyPatch) -> None:
    """Scanner should raise DeviceConnectionError on BLE failure."""
    mock_discover = AsyncMock(side_effect=Exception("BLE error"))
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    scanner = trn.BleakTrainerScanner()
    with pytest.raises(errors.DeviceError) as exc_info:
        await scanner.scan()

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

    scanner = trn.BleakTrainerScanner()
    trainers = await scanner.scan()

    assert len(trainers) == 1
    assert trainers[0].name == "Unknown"
    assert trainers[0].rssi == trainer.rssi


@pytest.mark.asyncio
async def test_detect_trainer_single_trainer_persists(monkeypatch: pytest.MonkeyPatch) -> None:
    """detect_trainer should persist and return trainer when exactly one found."""
    trainer = generate.trainer_info()
    mock_device = MagicMock()
    mock_device.name = trainer.name
    mock_device.address = trainer.address

    mock_adv = MagicMock()
    mock_adv.rssi = trainer.rssi

    mock_discover = AsyncMock(
        return_value={trainer.address: (mock_device, mock_adv)},
    )
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    # Mock AppConfig
    mock_config_handler = MagicMock()
    mock_config_handler.load_file.side_effect = FileNotFoundError("File not found")
    config_path = Path("/fake/config.toml")

    result = await trn.detect_trainer(mock_config_handler, config_path)

    assert result.name == trainer.name
    assert result.address == trainer.address
    assert result.rssi == trainer.rssi

    # Verify config was written with correct device_address
    mock_config_handler.write_file.assert_called_once()
    call_args = mock_config_handler.write_file.call_args
    assert call_args[0][0] == config_path
    written_config = call_args[0][1]
    assert written_config.device_address == trainer.address


@pytest.mark.asyncio
async def test_detect_trainer_preserves_ftp(monkeypatch: pytest.MonkeyPatch) -> None:
    """detect_trainer should preserve existing FTP value when updating device_address."""
    trainer = generate.trainer_info()
    mock_device = MagicMock()
    mock_device.name = trainer.name
    mock_device.address = trainer.address

    mock_adv = MagicMock()
    mock_adv.rssi = trainer.rssi

    mock_discover = AsyncMock(
        return_value={trainer.address: (mock_device, mock_adv)},
    )
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    # Mock AppConfig with existing FTP
    existing_ftp = generate.ftp()
    mock_config_handler = MagicMock()
    mock_config_handler.load_file.return_value = cfg.Config(
        ftp=existing_ftp,
        device_address=generate.mac_address(),
    )
    config_path = Path("/fake/config.toml")

    await trn.detect_trainer(mock_config_handler, config_path)

    # Verify config was written with preserved FTP
    mock_config_handler.write_file.assert_called_once()
    call_args = mock_config_handler.write_file.call_args
    written_config = call_args[0][1]
    assert written_config.device_address == trainer.address
    assert written_config.ftp == existing_ftp


@pytest.mark.asyncio
async def test_detect_trainer_no_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """detect_trainer should raise DeviceError when no trainers found."""
    mock_discover = AsyncMock(return_value={})
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    mock_config_handler = MagicMock()
    config_path = Path("/fake/config.toml")

    with pytest.raises(errors.DeviceError, match="No trainers found"):
        await trn.detect_trainer(mock_config_handler, config_path)

    # Verify config was not written
    mock_config_handler.write_file.assert_not_called()


@pytest.mark.asyncio
async def test_detect_trainer_multiple_trainers(monkeypatch: pytest.MonkeyPatch) -> None:
    """detect_trainer should raise DeviceError when multiple trainers found."""
    trainer1 = generate.trainer_info()
    trainer2 = generate.trainer_info()

    mock_device1 = MagicMock()
    mock_device1.name = trainer1.name
    mock_device1.address = trainer1.address
    mock_adv1 = MagicMock()
    mock_adv1.rssi = trainer1.rssi

    mock_device2 = MagicMock()
    mock_device2.name = trainer2.name
    mock_device2.address = trainer2.address
    mock_adv2 = MagicMock()
    mock_adv2.rssi = trainer2.rssi

    mock_discover = AsyncMock(
        return_value={
            trainer1.address: (mock_device1, mock_adv1),
            trainer2.address: (mock_device2, mock_adv2),
        },
    )
    monkeypatch.setattr("cytraco.trainer.bleak.BleakScanner.discover", mock_discover)

    mock_config_handler = MagicMock()
    config_path = Path("/fake/config.toml")

    with pytest.raises(errors.DeviceError, match="Found 2 trainers"):
        await trn.detect_trainer(mock_config_handler, config_path)

    # Verify config was not written
    mock_config_handler.write_file.assert_not_called()


@pytest.mark.asyncio
async def test_demo_power_meter_start() -> None:
    """DemoPowerMeter should start generating power data."""
    meter = trn.DemoPowerMeter()
    await meter.start()
    assert meter._running  # noqa: SLF001


@pytest.mark.asyncio
async def test_demo_power_meter_stop() -> None:
    """DemoPowerMeter should stop generating power data."""
    meter = trn.DemoPowerMeter()
    await meter.start()
    await meter.stop()
    assert not meter._running  # noqa: SLF001


@pytest.mark.asyncio
async def test_demo_power_meter_queue() -> None:
    """DemoPowerMeter queue should provide PowerData objects."""
    meter = trn.DemoPowerMeter(base_power=200, update_interval=0.01)
    await meter.start()
    data = await meter.queue.get()
    await meter.stop()
    assert data.power >= 0
    assert isinstance(data.power, int)


@pytest.mark.asyncio
async def test_demo_power_meter_power_range() -> None:
    """DemoPowerMeter should generate power within expected range."""
    base = 250
    meter = trn.DemoPowerMeter(base_power=base, update_interval=0.01)
    await meter.start()

    # Collect several samples
    samples = []
    for _ in range(10):
        data = await meter.queue.get()
        samples.append(data.power)

    await meter.stop()

    # All samples should be within reasonable range of base
    # (±15W variation + ±30W drift = max ±45W)
    for power in samples:
        assert base - 50 <= power <= base + 50


@pytest.mark.asyncio
async def test_demo_power_meter_restart() -> None:
    """DemoPowerMeter should handle multiple start/stop cycles."""
    meter = trn.DemoPowerMeter(update_interval=0.01)
    await meter.start()
    await meter.stop()
    await meter.start()
    data = await meter.queue.get()
    await meter.stop()
    assert data.power >= 0


@pytest.mark.asyncio
async def test_demo_power_meter_idempotent_start() -> None:
    """DemoPowerMeter should handle multiple start calls."""
    meter = trn.DemoPowerMeter()
    await meter.start()
    await meter.start()
    assert meter._running  # noqa: SLF001
    await meter.stop()
