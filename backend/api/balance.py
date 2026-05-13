from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from sandgravel_engine.process_flow import run_option

router = APIRouter()


class BalanceRequest(BaseModel):
    config_name: str = "option1"
    feed_grading: Optional[list[float]] = None
    system_throughput: Optional[float] = None

    @field_validator("feed_grading")
    @classmethod
    def check_grading_sum(cls, v):
        if v is not None:
            total = sum(v)
            if abs(total - 100.0) > 0.1:
                raise ValueError(f"Grading must sum to 100%, got {total}%")
        return v


@router.post("/balance/calculate")
async def calculate_balance(req: BalanceRequest):
    try:
        result = run_option(
            req.config_name,
            throughput=req.system_throughput,
            grading=req.feed_grading,
        )
        return {
            "streams": {
                name: {
                    "tonnage": stream.tonnage,
                    "grading": stream.grading.to_list(),
                }
                for name, stream in result.streams.items()
            },
            "equipment": [
                {
                    "model": e.model,
                    "quantity": e.quantity,
                    "unit_capacity": e.unit_capacity,
                    "actual_throughput": e.actual_throughput,
                    "load_factor": e.load_factor,
                }
                for e in result.equipment
            ],
            "products": result.products,
            "recirculation_gt40": result.recirc_gt40,
            "recirculation_20_5": result.recirc_20_5,
            "iterations": result.iterations,
            "convergence_error": result.error,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
