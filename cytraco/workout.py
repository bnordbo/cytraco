"""Workout protocols for power monitoring and training."""

import asyncio
from typing import Protocol

from cytraco.model.power import PowerData


class PowerMeter(Protocol):
    """Protocol for power meter monitoring.

    Classes implementing this protocol can monitor power data from cycling
    trainers or power meters. Power measurements are placed on a queue for
    consumption by clients such as UI components.
    """

    async def start(self) -> None:
        """Start power monitoring.

        Begins monitoring and placing PowerData objects on the queue.
        This method may initialize BLE connections and enable notifications.

        Raises:
            RuntimeError: If monitoring cannot be started or device is unavailable.
        """
        ...

    async def stop(self) -> None:
        """Stop power monitoring.

        Stops monitoring and disables notifications. The queue remains
        accessible for reading any remaining data.

        Raises:
            RuntimeError: If monitoring cannot be stopped cleanly.
        """
        ...

    def get_queue(self) -> asyncio.Queue[PowerData]:
        """Get the queue containing power measurements.

        Returns:
            Queue that receives PowerData objects as they are measured.
            Consumers should read from this queue to process power data.
        """
        ...
