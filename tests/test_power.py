"""Tests for power measurement model."""

from cytraco.model.power import PowerData
from tests import generators as generate


def test_power_data_creation() -> None:
    """PowerData should be created with generated data."""
    data = generate.power_data()
    assert isinstance(data, PowerData)
    assert isinstance(data.power, int)


def test_power_data_fields() -> None:
    """PowerData should provide access to power field."""
    power_value = generate.power_data().power
    assert 100 <= power_value <= 400
