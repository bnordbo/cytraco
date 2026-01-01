"""Tests for workout protocols."""

import asyncio

import pytest

from cytraco.model.power import PowerData
from cytraco.workout import PowerMeter
from tests import generators as generate


class MockPowerMeter:
    """Mock implementation of PowerMeter for testing."""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[PowerData] = asyncio.Queue()
        self._running = False

    async def start(self) -> None:
        """Mock start implementation."""
        self._running = True
        await self._queue.put(generate.power_data())

    async def stop(self) -> None:
        """Mock stop implementation."""
        self._running = False

    def get_queue(self) -> asyncio.Queue[PowerData]:
        """Mock get_queue implementation."""
        return self._queue


@pytest.mark.asyncio
async def test_power_meter_start() -> None:
    """PowerMeter implementations should start correctly."""
    meter: PowerMeter = MockPowerMeter()
    await meter.start()
    assert meter._running


@pytest.mark.asyncio
async def test_power_meter_stop() -> None:
    """PowerMeter implementations should stop correctly."""
    meter: PowerMeter = MockPowerMeter()
    await meter.start()
    await meter.stop()
    assert not meter._running


@pytest.mark.asyncio
async def test_power_meter_queue() -> None:
    """PowerMeter queue should contain PowerData objects."""
    meter: PowerMeter = MockPowerMeter()
    await meter.start()
    queue = meter.get_queue()
    data = await queue.get()
    assert isinstance(data, PowerData)
    assert isinstance(data.power, int)


@pytest.mark.asyncio
async def test_power_meter_type_check() -> None:
    """MockPowerMeter should satisfy PowerMeter protocol."""
    mock = MockPowerMeter()

    async def accepts_power_meter(pm: PowerMeter) -> asyncio.Queue[PowerData]:
        await pm.start()
        return pm.get_queue()

    queue = await accepts_power_meter(mock)
    assert isinstance(queue, asyncio.Queue)
