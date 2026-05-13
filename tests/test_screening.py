import pytest
from sandgravel_engine.screening import ScreenCalculator, ScreenParams, ScreenResult


def test_screen_pre_screening_80mm_dry():
    """Pre-screen 80mm dry: Excel Sheet4 rows 53-73"""
    params = ScreenParams(
        aperture=80, wet=False,
        basic_capacity=102, efficiency_factor=1.0, deck_factor=0.9,
        oversize_factor=1.1, undersize_factor=0.8, aperture_factor=1.0,
        condition_factor=1.0, shape_factor=0.85, moisture_factor=1.0,
        safety_factor=1.28, wet_factor=1.0,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=6.0, required_throughput=1500)
    assert abs(result.unit_capacity - 87.893) < 0.1
    assert abs(result.area - 14.4) < 0.1
    assert abs(result.capacity_per_unit - 1265.66) < 1
    assert result.num_units == 2
    assert abs(result.load_factor - 0.593) < 0.01


def test_screen_first_screening_40mm_wet():
    """First screen 40mm wet: Excel Sheet4 rows 98-118"""
    params = ScreenParams(
        aperture=40, wet=True,
        basic_capacity=65, efficiency_factor=0.85, deck_factor=0.9,
        oversize_factor=1.03, undersize_factor=1.0, aperture_factor=1.0,
        condition_factor=1.0, shape_factor=0.9, moisture_factor=1.0,
        safety_factor=1.18, wet_factor=1.0,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5, required_throughput=1640)
    assert abs(result.unit_capacity - 54.392) < 0.1
    assert abs(result.area - 18.0) < 0.1
    assert abs(result.capacity_per_unit - 979.06) < 1
    assert result.num_units == 2
    assert abs(result.load_factor - 0.838) < 0.01


def test_screen_first_screening_5mm_wet():
    """First screen 5mm wet: Excel Sheet4 rows 142-162"""
    params = ScreenParams(
        aperture=5, wet=True,
        basic_capacity=18, efficiency_factor=0.85, deck_factor=0.7,
        oversize_factor=1.42, undersize_factor=0.55, aperture_factor=1.2,
        condition_factor=1.0, shape_factor=0.95, moisture_factor=1.0,
        safety_factor=0.67, wet_factor=1.9,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5, required_throughput=690)
    assert abs(result.unit_capacity - 12.139) < 0.01
    assert result.num_units == 4
    assert abs(result.load_factor - 0.789) < 0.01


def test_screen_second_screening_5mm_dry():
    """Second screen 5mm dry: Excel Sheet4 rows 164-187"""
    params = ScreenParams(
        aperture=5, wet=False,
        basic_capacity=18, efficiency_factor=1.0, deck_factor=0.9,
        oversize_factor=1.4, undersize_factor=0.5, aperture_factor=1.0,
        condition_factor=0.9, shape_factor=0.95, moisture_factor=1.0,
        safety_factor=0.67, wet_factor=1.0,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5, required_throughput=1080)
    assert abs(result.unit_capacity - 6.496) < 0.01
    assert abs(result.area - 18.0) < 0.1
    assert abs(result.capacity_per_unit - 116.93) < 0.1
    assert result.num_units == 10
    assert abs(result.load_factor - 0.924) < 0.01


def test_screen_zero_throughput():
    """Zero required throughput should still compute correctly"""
    params = ScreenParams(
        aperture=40, wet=False,
        basic_capacity=65, efficiency_factor=1.0, deck_factor=1.0,
        oversize_factor=1.0, undersize_factor=1.0, aperture_factor=1.0,
        condition_factor=1.0, shape_factor=1.0, moisture_factor=1.0,
        safety_factor=1.0, wet_factor=1.0,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.0, screen_length=3.0, required_throughput=0)
    assert result.unit_capacity == 65.0
    assert result.num_units == 1
