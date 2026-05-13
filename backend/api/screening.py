from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ScreenCalcRequest(BaseModel):
    aperture: float
    wet: bool = False
    basic_capacity: float
    efficiency_factor: float = 1.0
    deck_factor: float = 0.9
    oversize_factor: float = 1.1
    undersize_factor: float = 0.8
    aperture_factor: float = 1.0
    condition_factor: float = 1.0
    shape_factor: float = 0.85
    moisture_factor: float = 1.0
    safety_factor: float = 1.28
    wet_factor: float = 1.0
    screen_width: float = 2.4
    screen_length: float = 6.0
    required_throughput: float = 0


@router.post("/screening/calculate")
async def calculate_screening(req: ScreenCalcRequest):
    from sandgravel_engine.screening import ScreenCalculator, ScreenParams

    params = ScreenParams(
        aperture=req.aperture, wet=req.wet,
        basic_capacity=req.basic_capacity, efficiency_factor=req.efficiency_factor,
        deck_factor=req.deck_factor, oversize_factor=req.oversize_factor,
        undersize_factor=req.undersize_factor, aperture_factor=req.aperture_factor,
        condition_factor=req.condition_factor, shape_factor=req.shape_factor,
        moisture_factor=req.moisture_factor, safety_factor=req.safety_factor,
        wet_factor=req.wet_factor,
    )
    calc = ScreenCalculator()
    result = calc.calculate(params, req.screen_width, req.screen_length, req.required_throughput)

    return {"unit_capacity": result.unit_capacity, "area": result.area,
            "capacity_per_unit": result.capacity_per_unit, "num_units": result.num_units,
            "load_factor": result.load_factor}
