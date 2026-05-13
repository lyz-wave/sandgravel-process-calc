import pytest
from sandgravel_engine.models import MaterialStream, SizeDistribution
from sandgravel_engine.balance import BalanceEngine, ProcessNode, FlowConfig, RecirculationSolver, ConvergenceError
from sandgravel_engine.crushing import JawCrusher
from sandgravel_engine.screening import Screen


def make_option1_feed():
    """Excel Sheet2 raw feed grading (69,12,7,7,3,2)"""
    return MaterialStream.from_percent("raw_feed", 1500, [69.0, 12.0, 7.0, 7.0, 3.0, 2.0])


def test_open_circuit_jaw_crusher():
    """Coarse crushing jaw e=150 open circuit: verify product grading"""
    feed = make_option1_feed()
    oversize = MaterialStream(name="grizzly_oversize", tonnage=feed.tonnage * 0.69,
                              grading=SizeDistribution(gt150=100, _150_80=0, _80_40=0, _40_20=0, _20_5=0, lt5=0))
    crusher = JawCrusher(closed_side_setting=150)
    product = crusher.crush(oversize)
    # Excel Sheet2 row 6: e=150 jaw product grading [14,33,25,12,10,6]
    expected = [14.0, 33.0, 25.0, 12.0, 10.0, 6.0]
    for i, (actual, exp) in enumerate(zip(product.grading.to_list(), expected)):
        assert abs(actual - exp) < 0.1, f"size[{i}]: {actual} != {exp}"


def test_balance_engine_open():
    """Open circuit balance: jaw crusher + pre-screen, no recirculation"""
    engine = BalanceEngine()
    feed = MaterialStream.from_percent("feed", 1500, [69, 12, 7, 7, 3, 2])

    nodes = [
        ProcessNode("jaw", "crusher", {"css": 150}),
        ProcessNode("pre_screen", "screen", {"aperture": 80}),
    ]
    edges = [
        ("feed", "jaw"),
        ("jaw", "pre_screen"),
    ]
    config = FlowConfig(nodes=nodes, edges=edges)

    result = engine.solve(feed, config)
    assert result.iterations >= 1
    assert result.convergence_error < 0.001


def test_convergence_error_raised():
    """ConvergenceError should be raised if max iterations exceeded"""
    solver = RecirculationSolver(max_iter=3, tol=1e-10)
    feed = MaterialStream.from_percent("feed", 1500, [69, 12, 7, 7, 3, 2])

    def process_fn(s):
        return MaterialStream(name="product", tonnage=s.tonnage * 1.5, grading=s.grading)
    def recirc_fn(s):
        return s
    def ratio_fn(s):
        return 0.5  # 50% recirculates — will never converge with tol=1e-10

    with pytest.raises(ConvergenceError):
        solver.solve(feed, process_fn, recirc_fn, ratio_fn)
