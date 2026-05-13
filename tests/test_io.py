import pytest
import tempfile
import os
import json
from sandgravel_engine.io import load_yaml_config, export_to_excel, import_from_excel, export_to_json
from sandgravel_engine.models import BalanceResult, MaterialStream, SizeDistribution, EquipmentSelection


def test_load_option1_yaml():
    config = load_yaml_config("option1")
    assert config["system_throughput"] == 1500
    assert abs(config["feed_grading"]["gt150"] - 69.0) < 0.01
    assert config["jaw_crusher"]["css"] == 150


def test_load_option2_yaml():
    config = load_yaml_config("option2")
    assert config["system_throughput"] == 1100
    assert abs(config["feed_grading"]["_40_20"] - 30.8) < 0.01


def test_export_import_roundtrip():
    """Excel export then import preserves data"""
    sd = SizeDistribution(gt150=9.66, _150_80=34.77, _80_40=24.25, _40_20=15.28, _20_5=9.9, lt5=6.14)
    ms = MaterialStream(name="test", tonnage=1500, grading=sd)
    eq = [EquipmentSelection("Ci125", 3, 500, 1200)]
    br = BalanceResult(streams={"feed": ms}, equipment=eq, iterations=5, convergence_error=0.00001)

    path = os.path.join(tempfile.gettempdir(), "test_roundtrip.xlsx")
    try:
        export_to_excel(br, path)
        assert os.path.exists(path)
        imported = import_from_excel(path)
        assert "feed" in imported.streams
        assert abs(imported.streams["feed"].tonnage - 1500) < 0.01
        assert imported.iterations == 5
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_export_to_json():
    sd = SizeDistribution(gt150=9.66, _150_80=34.77, _80_40=24.25, _40_20=15.28, _20_5=9.9, lt5=6.14)
    ms = MaterialStream(name="feed", tonnage=1500, grading=sd)
    eq = [EquipmentSelection("Ci125", 3, 500, 1200)]
    br = BalanceResult(streams={"feed": ms}, equipment=eq, iterations=5, convergence_error=0.00001)

    json_str = export_to_json(br)
    data = json.loads(json_str)
    assert data["iterations"] == 5
    assert "feed" in data["streams"]


def test_load_nonexistent_config():
    with pytest.raises(FileNotFoundError):
        load_yaml_config("nonexistent_option")


def test_export_empty_result():
    br = BalanceResult(streams={}, equipment=[], iterations=0, convergence_error=0.0)
    path = os.path.join(tempfile.gettempdir(), "test_empty.xlsx")
    try:
        export_to_excel(br, path)
        assert os.path.exists(path)
    finally:
        if os.path.exists(path):
            os.unlink(path)
