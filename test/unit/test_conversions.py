import pytest

from ha_broker_dashboard.conversions import (
    celsius_to_fahrenheit,
    convert_value,
    fahrenheit_to_celsius,
    feet_to_meters,
    has_conversion,
    meters_to_feet,
    truncate_to_precision,
)


class TestTruncateToPrecision:
    def test_truncate_to_hundredths(self):
        assert truncate_to_precision(19.343, 0.01) == 19.34

    def test_truncate_to_tenths(self):
        assert truncate_to_precision(19.343, 0.1) == 19.3

    def test_truncate_to_whole_numbers(self):
        assert truncate_to_precision(19.343, 1) == 19.0

    def test_truncate_to_half_units(self):
        assert truncate_to_precision(19.343, 0.5) == 19.0
        assert truncate_to_precision(19.75, 0.5) == 19.5

    def test_truncate_negative_value(self):
        assert truncate_to_precision(-19.343, 0.01) == -19.35

    def test_truncate_zero_precision_returns_original(self):
        assert truncate_to_precision(19.343, 0) == 19.343

    def test_truncate_negative_precision_returns_original(self):
        assert truncate_to_precision(19.343, -0.01) == 19.343


class TestCelsiusToFahrenheit:
    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32

    def test_boiling_point(self):
        assert celsius_to_fahrenheit(100) == 212

    def test_body_temperature(self):
        assert celsius_to_fahrenheit(37) == pytest.approx(98.6)

    def test_negative_temperature(self):
        assert celsius_to_fahrenheit(-40) == -40


class TestFahrenheitToCelsius:
    def test_freezing_point(self):
        assert fahrenheit_to_celsius(32) == 0

    def test_boiling_point(self):
        assert fahrenheit_to_celsius(212) == 100

    def test_body_temperature(self):
        assert fahrenheit_to_celsius(98.6) == pytest.approx(37)

    def test_negative_temperature(self):
        assert fahrenheit_to_celsius(-40) == -40


class TestMetersToFeet:
    def test_one_meter(self):
        assert meters_to_feet(1) == pytest.approx(3.28084)

    def test_zero(self):
        assert meters_to_feet(0) == 0

    def test_negative_value(self):
        assert meters_to_feet(-1) == pytest.approx(-3.28084)


class TestFeetToMeters:
    def test_one_foot(self):
        assert feet_to_meters(1) == pytest.approx(0.3048, rel=1e-3)

    def test_zero(self):
        assert feet_to_meters(0) == 0

    def test_round_trip(self):
        original = 10.5
        assert feet_to_meters(meters_to_feet(original)) == pytest.approx(original)


class TestConvertValue:
    def test_celsius_to_fahrenheit(self):
        assert convert_value(0, "°C", "°F") == 32

    def test_fahrenheit_to_celsius(self):
        assert convert_value(32, "°F", "°C") == 0

    def test_alternative_unit_symbols(self):
        assert convert_value(0, "C", "F") == 32
        assert convert_value(32, "F", "C") == 0

    def test_meters_to_feet(self):
        assert convert_value(1, "m", "ft") == pytest.approx(3.28084)

    def test_feet_to_meters(self):
        assert convert_value(1, "ft", "m") == pytest.approx(0.3048, rel=1e-3)

    def test_same_unit_returns_original(self):
        assert convert_value(42.5, "°C", "°C") == 42.5

    def test_none_input_unit_returns_original(self):
        assert convert_value(42.5, None, "°F") == 42.5

    def test_none_output_unit_returns_original(self):
        assert convert_value(42.5, "°C", None) == 42.5

    def test_unknown_conversion_returns_original(self):
        assert convert_value(42.5, "foo", "bar") == 42.5


class TestHasConversion:
    def test_valid_conversion_exists(self):
        assert has_conversion("°C", "°F") is True
        assert has_conversion("m", "ft") is True

    def test_same_unit_returns_true(self):
        assert has_conversion("°C", "°C") is True

    def test_none_input_returns_false(self):
        assert has_conversion(None, "°F") is False

    def test_none_output_returns_false(self):
        assert has_conversion("°C", None) is False

    def test_unknown_conversion_returns_false(self):
        assert has_conversion("foo", "bar") is False

