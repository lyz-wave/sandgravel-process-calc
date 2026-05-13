import pytest
from sandgravel_engine.equipment import EquipmentDB, EquipmentSpec, select_crusher, select_screen


def test_equipment_db_has_jaw_crushers():
    db = EquipmentDB()
    jaw = db.get_by_type("jaw_crusher")
    assert any(c.model == "Ci125" for c in jaw)


def test_equipment_db_has_cone_crushers():
    db = EquipmentDB()
    cone = db.get_by_type("cone_crusher")
    assert any(c.model == "Ci225" for c in cone)


def test_equipment_db_get_by_model():
    db = EquipmentDB()
    spec = db.get_by_model("Ci125")
    assert spec is not None
    assert spec.unit_capacity == 500
    assert spec.max_feed_size == 800


def test_select_jaw_crusher_1200tph():
    """Excel Sheet2 row 56: 1200 T/H → 3x Ci125"""
    result = select_crusher("jaw", 1200)
    assert result.model == "Ci125"
    assert result.quantity == 3
    assert abs(result.load_factor - 0.8) < 0.01


def test_select_cone_crusher_817tph():
    """Excel Sheet2 row 58: 817 T/H → 3x Ci225"""
    result = select_crusher("cone", 817)
    assert result.model == "Ci225"
    assert result.quantity == 3
    assert abs(result.load_factor - 0.65) < 0.03


def test_select_vsi_1080tph():
    """Excel Sheet2 row 60: 1080 T/H → 6x PL9500"""
    result = select_crusher("vsi", 1080)
    assert result.model == "PL9500"
    assert result.quantity == 6


def test_select_screen_default_params():
    result = select_screen(1500, aperture=80, wet=False)
    assert result.quantity >= 1
    assert result.load_factor > 0


def test_select_unknown_crusher_type():
    with pytest.raises(ValueError, match="无可用"):
        select_crusher("hammer", 1000)
