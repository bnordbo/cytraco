"""Configuration model for Cytraco."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration.

    Attributes:
        device_address: Bluetooth address of the trainer device (e.g., MAC address).
        ftp: Functional Threshold Power in watts.
    """

    device_address: str | None = None
    ftp: int | None = None
