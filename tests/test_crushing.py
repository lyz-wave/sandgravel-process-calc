import pytest
from sandgravel_engine.models import MaterialStream, SizeDistribution
from sandgravel_engine.crushing import JawCrusher, ConeCrusher, VSICrusher


def test_jaw_crusher_e150_product():
    """Excel Sheet2 row 6: e=150 jaw product grading [14,33,25,12,10,6]"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1035, SizeDistribution(gt150=100))
    product = crusher.crush(feed)
    expected = [14.0, 33.0, 25.0, 12.0, 10.0, 6.0]
    for i, (actual, exp) in enumerate(zip(product.grading.to_list(), expected)):
        assert abs(actual - exp) < 0.1, f"size[{i}] actual={actual} expected={exp}"


def test_jaw_crusher_mass_conservation():
    """Mass conservation: product tonnage == feed tonnage"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1000, SizeDistribution(gt150=80, _150_80=20))
    product = crusher.crush(feed)
    assert abs(product.tonnage - 1000) < 0.01


def test_jaw_crusher_product_sums_to_100():
    """Jaw e=150 product grading should sum to 100%"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1000, SizeDistribution(gt150=100))
    product = crusher.crush(feed)
    assert abs(product.grading.total() - 100) < 0.1


def test_cone_crusher_e40_product():
    """Excel Sheet2 row 10: e=40 cone product grading 0,0,17,28,38,17"""
    crusher = ConeCrusher(closed_side_setting=40)
    feed = MaterialStream("feed", 500, SizeDistribution(gt150=10, _150_80=50, _80_40=40))
    product = crusher.crush(feed)
    expected = [0.0, 0.0, 17.0, 28.0, 38.0, 17.0]
    for i, (actual, exp) in enumerate(zip(product.grading.to_list(), expected)):
        assert abs(actual - exp) < 0.1, f"size[{i}] actual={actual} expected={exp}"


def test_cone_crusher_mass_conservation():
    crusher = ConeCrusher(closed_side_setting=40)
    feed = MaterialStream("feed", 500, SizeDistribution(gt150=0, _150_80=30, _80_40=70))
    product = crusher.crush(feed)
    assert abs(product.tonnage - 500) < 0.01


def test_vsi_crusher_product_ratio():
    """PL9500 produces 20:50:30 for 40-20, 20-5, <5"""
    crusher = VSICrusher(model="PL9500")
    feed = MaterialStream("feed", 1000, SizeDistribution(_40_20=50, _20_5=50))
    product = crusher.crush(feed)
    assert abs(product.grading._40_20 - 20) < 0.1
    assert abs(product.grading._20_5 - 50) < 0.1
    assert abs(product.grading.lt5 - 30) < 0.1
    assert abs(product.grading.total() - 100) < 0.1


def test_vsi_crusher_mass_conservation():
    crusher = VSICrusher(model="PL9500")
    feed = MaterialStream("feed", 800, SizeDistribution(_40_20=60, _20_5=40))
    product = crusher.crush(feed)
    assert abs(product.tonnage - 800) < 0.01
