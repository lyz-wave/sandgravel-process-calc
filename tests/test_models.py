import pytest
from sandgravel_engine.models import SizeDistribution, MaterialStream, EquipmentSelection, BalanceResult


def test_size_distribution_total():
    sd = SizeDistribution(gt150=9.66, _150_80=34.77, _80_40=24.25,
                          _40_20=15.28, _20_5=9.9, lt5=6.14)
    assert abs(sd.total() - 100.0) < 0.01


def test_size_distribution_add():
    a = SizeDistribution(gt150=10, _150_80=20, _80_40=30,
                         _40_20=20, _20_5=15, lt5=5)
    b = SizeDistribution(gt150=5, _150_80=10, _80_40=15,
                         _40_20=30, _20_5=25, lt5=15)
    c = a + b
    assert abs(c.gt150 - 15) < 0.01
    assert abs(c._40_20 - 50) < 0.01


def test_size_distribution_mul():
    sd = SizeDistribution(gt150=10, _150_80=20, _80_40=30,
                          _40_20=20, _20_5=15, lt5=5)
    result = sd * 0.5
    assert abs(result.gt150 - 5) < 0.01
    assert abs(result._80_40 - 15) < 0.01


def test_material_stream_from_percent():
    ms = MaterialStream.from_percent("test", 1500, [9.66, 34.77, 24.25, 15.28, 9.9, 6.14])
    assert ms.tonnage == 1500
    assert abs(ms.grading.gt150 - 9.66) < 0.01


def test_material_stream_tonnage_by_size():
    sd = SizeDistribution(gt150=10, _150_80=20, _80_40=30,
                          _40_20=20, _20_5=15, lt5=5)
    ms = MaterialStream(name="test", tonnage=1000, grading=sd)
    assert abs(ms.tonnage_gt80() - 300) < 0.01  # (10+20)% of 1000
    assert abs(ms.tonnage_lt40() - 400) < 0.01  # (20+15+5)% of 1000


def test_equipment_selection_load_factor():
    eq = EquipmentSelection(model="Ci125", quantity=3, unit_capacity=500, actual_throughput=1200)
    assert abs(eq.load_factor - 0.8) < 0.01


def test_balance_result_to_dict():
    sd = SizeDistribution(gt150=10, _150_80=20, _80_40=30, _40_20=20, _20_5=15, lt5=5)
    ms = MaterialStream(name="feed", tonnage=1500, grading=sd)
    eq = [EquipmentSelection(model="Ci125", quantity=3, unit_capacity=500, actual_throughput=1200)]
    br = BalanceResult(streams={"feed": ms}, equipment=eq, iterations=5, convergence_error=0.00001)
    d = br.to_dict()
    assert "feed" in d["streams"]
    assert d["iterations"] == 5
