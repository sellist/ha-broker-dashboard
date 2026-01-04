"""Unit conversion module for sensor data."""

import math
from typing import Callable


def truncate_to_precision(value: float, precision: float) -> float:
    if precision <= 0:
        return value
    return math.floor(value / precision) * precision


def celsius_to_fahrenheit(value: float) -> float:
    return (value * 9 / 5) + 32


def fahrenheit_to_celsius(value: float) -> float:
    return (value - 32) * 5 / 9


def meters_to_feet(value: float) -> float:
    return value * 3.28084


def feet_to_meters(value: float) -> float:
    return value / 3.28084


CONVERSIONS: dict[str, Callable[[float], float]] = {
    "°C_to_°F": celsius_to_fahrenheit,
    "°F_to_°C": fahrenheit_to_celsius,
    "C_to_F": celsius_to_fahrenheit,
    "F_to_C": fahrenheit_to_celsius,
    "m_to_ft": meters_to_feet,
    "ft_to_m": feet_to_meters,
}


def convert_value(value: float, input_unit: str | None, output_unit: str | None) -> float:
    if input_unit is None or output_unit is None:
        return value

    if input_unit == output_unit:
        return value

    conversion_key = f"{input_unit}_to_{output_unit}"

    if conversion_key in CONVERSIONS:
        return CONVERSIONS[conversion_key](value)

    return value


def has_conversion(input_unit: str | None, output_unit: str | None) -> bool:
    if input_unit is None or output_unit is None:
        return False
    if input_unit == output_unit:
        return True
    conversion_key = f"{input_unit}_to_{output_unit}"
    return conversion_key in CONVERSIONS

