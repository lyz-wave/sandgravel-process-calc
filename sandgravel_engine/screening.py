from dataclasses import dataclass
from .models import MaterialStream


@dataclass
class ScreenParams:
    """Screen calculation input parameters for BEDVHTKPWSM formula"""
    aperture: float
    wet: bool
    basic_capacity: float       # B: basic screen capacity t/m²·h
    efficiency_factor: float    # E: screen efficiency correction
    deck_factor: float          # D: screen deck position correction
    oversize_factor: float      # V: oversize material correction
    undersize_factor: float     # H: undersize material correction
    aperture_factor: float      # T: screen aperture correction
    condition_factor: float     # K: material condition correction
    shape_factor: float         # P: particle shape correction
    moisture_factor: float      # W: moisture correction
    safety_factor: float        # S: safety factor
    wet_factor: float           # M: wet screening correction (1.0 for dry)


@dataclass
class ScreenResult:
    """Screen calculation result"""
    unit_capacity: float         # Q: unit area capacity t/m²·h
    area: float                  # required screen area per unit m²
    capacity_per_unit: float     # capacity per screen unit t/h
    num_units: int               # number of screens needed
    load_factor: float           # utilization ratio
    required_throughput: float   # required throughput t/h


class ScreenCalculator:
    """Vibrating screen equipment sizing calculator
    Q = B * E * D * V * H * T * K * P * W * S * M
    """

    def calculate(self, params: ScreenParams, screen_width: float,
                  screen_length: float, required_throughput: float = 0.0) -> ScreenResult:
        # Q = B * E * D * V * H * T * K * P * W * S * M
        Q = (
            params.basic_capacity *
            params.efficiency_factor *
            params.deck_factor *
            params.oversize_factor *
            params.undersize_factor *
            params.aperture_factor *
            params.condition_factor *
            params.shape_factor *
            params.moisture_factor *
            params.safety_factor *
            params.wet_factor
        )

        area_per_unit = screen_width * screen_length
        capacity_per_unit = area_per_unit * Q

        if required_throughput <= 0:
            num_units = 1
        else:
            num_units = max(1, int(required_throughput / capacity_per_unit) +
                           (1 if required_throughput % capacity_per_unit > 1e-6 else 0))

        actual_total_capacity = num_units * capacity_per_unit
        load_factor = required_throughput / actual_total_capacity if required_throughput > 0 else 0.0

        return ScreenResult(
            unit_capacity=Q,
            area=area_per_unit,
            capacity_per_unit=capacity_per_unit,
            num_units=num_units,
            load_factor=load_factor,
            required_throughput=required_throughput,
        )


# Preserve the original Screen class for backward compatibility with balance.py
class Screen:
    def __init__(self, aperture: float):
        self.aperture = aperture

    def oversize(self, feed: MaterialStream) -> MaterialStream:
        # Return portion above aperture
        return MaterialStream(name=f"{feed.name}_oversize", tonnage=feed.tonnage * 0.3, grading=feed.grading)
