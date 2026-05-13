from fastapi import APIRouter

router = APIRouter()


@router.post("/equipment/select")
async def select_equipment(req: dict):
    from sandgravel_engine.equipment import select_crusher, select_screen

    eq_type = req.get("type")
    throughput = req.get("throughput", 0)

    try:
        if eq_type in ("jaw", "cone", "vsi"):
            result = select_crusher(eq_type, throughput)
        elif eq_type == "screen":
            result = select_screen(throughput, req.get("aperture", 40), req.get("wet", False))
        else:
            return {"error": f"Unknown equipment type: {eq_type}"}

        return {"model": result.model, "quantity": result.quantity,
                "unit_capacity": result.unit_capacity, "load_factor": result.load_factor}
    except Exception as e:
        return {"error": str(e)}
