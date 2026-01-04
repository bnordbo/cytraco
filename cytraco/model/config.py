"""Configuration model for Cytraco. Alias: cfg."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration.

    Attributes:
        ftp: Functional Threshold Power in watts.
        device_address: Bluetooth address of the trainer device (e.g., MAC address).
        demo: Runtime flag for demo mode (not persisted to file).
    """

    ftp: int
    device_address: str | None = None
    demo: bool = False
