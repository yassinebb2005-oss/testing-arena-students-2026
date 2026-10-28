"""Tests for the weather module (see TEST_PLAN.md)."""

import pytest

from weather import (
    average_temperature,
    filter_by_temperature,
    hottest_measurement,
    parse_measurement,
    parse_time,
)


# parse_time


def test_parse_time_valid():
    assert parse_time("14:21") == 861
    assert parse_time("00:00") == 0
    assert parse_time("00:59") == 59
    assert parse_time("01:00") == 60
    assert parse_time("23:59") == 1439
    assert parse_time("9:5") == 545


def test_parse_time_invalid():
    for text in ["24:00", "12:60", "-1:30", "1430", "12:30:45", "12:", "ab:cd", " 12:30"]:
        with pytest.raises(ValueError):
            parse_time(text)


# parse_measurement


def test_parse_measurement_valid():
    assert parse_measurement("Köln;14:21;21.7") == ("Köln", 861, 21.7)
    assert parse_measurement("Berlin;06:00;-5.5") == ("Berlin", 360, -5.5)
    assert parse_measurement("Bad Honnef;10:00;15.0") == ("Bad Honnef", 600, 15.0)


def test_parse_measurement_temperature_is_float():
    assert isinstance(parse_measurement("Bonn;08:30;20")[2], float)


def test_parse_measurement_strips_whitespace():
    assert parse_measurement(" Köln ; 14:21 ; 21.7 ") == ("Köln", 861, 21.7)
    assert parse_measurement("Köln; 14:21;21.7") == ("Köln", 861, 21.7)


def test_parse_measurement_invalid():
    for line in [
        None,
        123,
        "Köln;14:21",
        "Köln;14:21;21.7;x",
        "   ;14:21;1.0",
        "Köln;25:00;1.0",
        "Köln;14:21;abc",
    ]:
        with pytest.raises(ValueError):
            parse_measurement(line)


# filter_by_temperature


def test_filter_by_temperature_bounds_are_inclusive():
    measurements = [("A", 1, 14.9), ("B", 2, 15.0), ("C", 3, 20.0), ("D", 4, 20.1)]

    assert filter_by_temperature(measurements, 15.0, 20.0) == [
        ("B", 2, 15.0),
        ("C", 3, 20.0),
    ]


def test_filter_by_temperature_equal_bounds():
    measurements = [("A", 1, 9.9), ("B", 2, 10.0), ("C", 3, 10.1)]

    assert filter_by_temperature(measurements, 10.0, 10.0) == [("B", 2, 10.0)]


def test_filter_by_temperature_no_match():
    assert filter_by_temperature([], 0.0, 10.0) == []
    assert filter_by_temperature([("A", 1, 1.0)], 5.0, 10.0) == []


def test_filter_by_temperature_lower_greater_than_upper():
    with pytest.raises(ValueError):
        filter_by_temperature([("A", 1, 5.0)], 20.0, 10.0)


def test_filter_by_temperature_keeps_order_and_input():
    measurements = [("A", 3, 5.0), ("B", 1, 9.0), ("A", 3, 5.0)]

    result = filter_by_temperature(measurements, 0.0, 10.0)

    assert result == [("A", 3, 5.0), ("B", 1, 9.0), ("A", 3, 5.0)]
    assert result is not measurements


# average_temperature


def test_average_temperature_only_matching_city():
    measurements = [
        ("Köln", 600, 10.0),
        ("Köln", 700, 11.0),
        ("Köln", 800, 15.0),
        ("Bonn", 900, 0.0),
    ]

    assert average_temperature(measurements, "Köln") == pytest.approx(12.0)


def test_average_temperature_no_matching_city():
    measurements = [("Köln", 600, 10.0)]

    with pytest.raises(ValueError):
        average_temperature(measurements, "Bonn")
    with pytest.raises(ValueError):
        average_temperature(measurements, "köln")
    with pytest.raises(ValueError):
        average_temperature([], "Köln")


# hottest_measurement


def test_hottest_measurement_unique_maximum():
    first = [("A", 100, 30.0), ("B", 200, 20.0), ("C", 300, 10.0)]
    middle = [("A", 100, 10.0), ("B", 200, 30.0), ("C", 300, 20.0)]
    last = [("A", 100, 10.0), ("B", 200, 20.0), ("C", 300, 30.0)]

    assert hottest_measurement(first) == ("A", 100, 30.0)
    assert hottest_measurement(middle) == ("B", 200, 30.0)
    assert hottest_measurement(last) == ("C", 300, 30.0)


def test_hottest_measurement_negative_temperatures():
    measurements = [("A", 1, -10.0), ("B", 2, -2.0), ("C", 3, -5.0)]

    assert hottest_measurement(measurements) == ("B", 2, -2.0)


def test_hottest_measurement_tie_prefers_earliest_time():
    earlier_first = [("A", 100, 20.0), ("B", 200, 20.0)]
    earlier_last = [("A", 300, 20.0), ("B", 100, 20.0), ("C", 200, 20.0)]

    assert hottest_measurement(earlier_first) == ("A", 100, 20.0)
    assert hottest_measurement(earlier_last) == ("B", 100, 20.0)


def test_hottest_measurement_tie_on_lower_temperature_is_ignored():
    measurements = [("A", 500, 30.0), ("B", 100, 20.0), ("C", 50, 20.0)]

    assert hottest_measurement(measurements) == ("A", 500, 30.0)


def test_hottest_measurement_same_temperature_and_time_first_listed_wins():
    measurements = [("Köln", 600, 25.0), ("Bonn", 600, 25.0)]

    assert hottest_measurement(measurements) == ("Köln", 600, 25.0)


def test_hottest_measurement_empty_input():
    with pytest.raises(ValueError):
        hottest_measurement([])
