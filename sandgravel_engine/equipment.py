from dataclasses import dataclass
from typing import Optional
from .models import EquipmentSelection


@dataclass
class EquipmentSpec:
    """Equipment specification"""
    model: str
    eq_type: str  # "jaw_crusher", "cone_crusher", "vsi", "screen", "sand_recovery"
    unit_capacity: float  # t/h
    screen_area: Optional[float] = None  # m² (screens only)
    screen_layers: Optional[int] = None
    max_feed_size: Optional[float] = None  # mm
    power: Optional[float] = None  # kW


# Equipment database from Excel source documents
_DEFAULT_EQUIPMENT = [
    EquipmentSpec("Ci125", "jaw_crusher", 500, max_feed_size=800, power=160),
    EquipmentSpec("Ci225", "cone_crusher", 420, max_feed_size=250, power=220),
    EquipmentSpec("PL9500", "vsi", 180, max_feed_size=40, power=500),
    EquipmentSpec("PL8500", "sand_recovery", 95, max_feed_size=5, power=264),
    EquipmentSpec("2YKR3060", "screen", 0, screen_area=18, screen_layers=2),
    EquipmentSpec("3YKR2472", "screen", 0, screen_area=18, screen_layers=3),
    EquipmentSpec("2YKR2472", "screen", 0, screen_area=18, screen_layers=2),
]


class EquipmentDB:
    """Equipment database"""

    def __init__(self, equipment: list[EquipmentSpec] = None):
        self._equipment = equipment or _DEFAULT_EQUIPMENT

    def get_by_type(self, eq_type: str) -> list[EquipmentSpec]:
        return [e for e in self._equipment if e.eq_type == eq_type]

    def get_by_model(self, model: str) -> Optional[EquipmentSpec]:
        for e in self._equipment:
            if e.model == model:
                return e
        return None


def select_crusher(crusher_type: str, required_throughput: float,
                   db: EquipmentDB = None) -> EquipmentSelection:
    """Select crusher model and quantity"""
    if db is None:
        db = EquipmentDB()

    type_map = {"jaw": "jaw_crusher", "cone": "cone_crusher", "vsi": "vsi"}
    eq_type = type_map.get(crusher_type, crusher_type)
    candidates = sorted(db.get_by_type(eq_type), key=lambda e: e.unit_capacity, reverse=True)

    if not candidates:
        raise ValueError(f"无可用{crusher_type}破碎机")

    best = candidates[0]
    num_units = max(1, round(required_throughput / best.unit_capacity) +
                   (1 if required_throughput % best.unit_capacity > 1e-6 else 0))

    return EquipmentSelection(
        model=best.model,
        quantity=num_units,
        unit_capacity=best.unit_capacity,
        actual_throughput=required_throughput,
    )


def select_screen(required_throughput: float, aperture: float, wet: bool = False,
                  db: EquipmentDB = None) -> EquipmentSelection:
    """Select screen model and quantity"""
    if db is None:
        db = EquipmentDB()

    from .screening import ScreenCalculator, ScreenParams

    if aperture >= 60:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=80,
            efficiency_factor=1.0, deck_factor=0.9, oversize_factor=1.1, undersize_factor=0.5,
            aperture_factor=0.8, condition_factor=1.0, shape_factor=0.85, moisture_factor=1.0,
            safety_factor=1.28, wet_factor=1.0)
    elif aperture >= 40:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=65,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.9 if wet else 0.8,
            oversize_factor=1.03 if wet else 1.1, undersize_factor=1.0 if wet else 0.75,
            aperture_factor=1.0, condition_factor=1.0, shape_factor=0.9, moisture_factor=1.0,
            safety_factor=1.18, wet_factor=1.0)
    elif aperture >= 20:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=48,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.8,
            oversize_factor=1.08 if wet else 1.4, undersize_factor=0.8 if wet else 0.6,
            aperture_factor=1.0, condition_factor=1.0, shape_factor=0.9, moisture_factor=1.0,
            safety_factor=0.99 if wet else 1.28, wet_factor=1.0)
    else:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=18,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.7 if wet else 0.9,
            oversize_factor=1.42 if wet else 1.4, undersize_factor=0.55 if wet else 0.5,
            aperture_factor=1.2 if wet else 1.0, condition_factor=1.0, shape_factor=0.95,
            moisture_factor=1.0, safety_factor=0.67, wet_factor=1.9 if wet else 1.0)

    calc = ScreenCalculator()
    if aperture >= 40:
        width, length = 2.4, 6.0
    else:
        width, length = 2.4, 7.5

    result = calc.calculate(params, width, length, required_throughput)

    # Select screen model
    if aperture >= 20:
        model = "2YKR3060" if aperture >= 60 else "3YKR2472"
    else:
        model = "2YKR2472"

    return EquipmentSelection(
        model=model,
        quantity=result.num_units,
        unit_capacity=result.capacity_per_unit,
        actual_throughput=required_throughput,
    )
