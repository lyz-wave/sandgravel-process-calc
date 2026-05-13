from fastapi import APIRouter, UploadFile, File
from fastapi.responses import FileResponse
import tempfile
import os

router = APIRouter()


@router.post("/io/import-excel")
async def import_excel(file: UploadFile = File(...)):
    from sandgravel_engine.io import import_from_excel

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        content = await file.read()
        f.write(content)
        path = f.name

    try:
        result = import_from_excel(path)
        return result.to_dict()
    finally:
        os.unlink(path)


@router.post("/io/export-excel")
async def export_excel(data: dict):
    from sandgravel_engine.io import export_to_excel
    from sandgravel_engine.models import BalanceResult, MaterialStream, SizeDistribution, EquipmentSelection

    streams = {}
    for name, s in data.get("streams", {}).items():
        streams[name] = MaterialStream(
            name=name, tonnage=s.get("tonnage", 0),
            grading=SizeDistribution.from_list(s.get("grading", [0]*6)))

    equipment = [EquipmentSelection(model=e["model"], quantity=e["quantity"],
                  unit_capacity=e["unit_capacity"], actual_throughput=e.get("actual_throughput", 0))
                 for e in data.get("equipment", [])]

    result = BalanceResult(streams=streams, equipment=equipment,
                          iterations=data.get("iterations", 0),
                          convergence_error=data.get("convergence_error", 0))

    path = tempfile.mktemp(suffix=".xlsx")
    export_to_excel(result, path)
    return FileResponse(path, filename="balance_result.xlsx",
                        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
