import pytest
import sys
sys.path.insert(0, r"C:\Users\Admin\Desktop\砂石系统")
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)


def test_get_options():
    response = client.get("/api/options")
    assert response.status_code == 200
    data = response.json()
    assert "configs" in data
    assert "option1" in data["configs"]


def test_balance_calculate_option1():
    response = client.post("/api/balance/calculate", json={"config_name": "option1"})
    assert response.status_code == 200
    data = response.json()
    assert "streams" in data
    assert data["iterations"] > 0


def test_balance_validate_grading():
    bad_config = {"config_name": "option1", "feed_grading": [50, 20, 10, 5, 5, 5]}
    response = client.post("/api/balance/calculate", json=bad_config)
    assert response.status_code == 422


def test_equipment_select():
    response = client.post("/api/equipment/select", json={"type": "jaw", "throughput": 1200})
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "Ci125"


def test_screening_calculate():
    response = client.post("/api/screening/calculate", json={
        "aperture": 80, "wet": False, "basic_capacity": 102,
        "efficiency_factor": 1.0, "deck_factor": 0.9, "oversize_factor": 1.1,
        "undersize_factor": 0.8, "aperture_factor": 1.0, "condition_factor": 1.0,
        "shape_factor": 0.85, "moisture_factor": 1.0, "safety_factor": 1.28,
        "wet_factor": 1.0, "screen_width": 2.4, "screen_length": 6.0,
        "required_throughput": 1500
    })
    assert response.status_code == 200
    data = response.json()
    assert data["num_units"] >= 1
