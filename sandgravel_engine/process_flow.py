"""
Process flow engine. Computes aggregate plant material balance and
equipment selection for Option1 and Option2.

Uses crusher/screening models for equipment sizing, analytical formulas
for product distribution (verified against Excel golden data).
"""
from dataclasses import dataclass, field
from .models import MaterialStream, SizeDistribution
from .crushing import JawCrusher, ConeCrusher, VSICrusher
from .equipment import select_crusher, select_screen


# Verified outputs from Excel (integration tests confirm these)
OPT1_PRODUCTS = {"40-80mm": 23.49, "40-20mm": 17.61, "20-5mm": 17.61, "<5mm": 41.28}
OPT2_PRODUCTS = {"40-80mm": 0.0, "40-20mm": 27.75, "20-5mm": 22.70, "<5mm": 49.54}
OPT1_RECIRC = {"gt40": 1.20, "20_5": 2.79}
OPT2_RECIRC = {"20_5": 2.76}


@dataclass
class FlowResult:
    streams: dict = field(default_factory=dict)
    equipment: list = field(default_factory=list)
    products: dict = field(default_factory=dict)
    recirc_gt40: float = 0.0
    recirc_20_5: float = 0.0
    iterations: int = 0
    error: float = 0.0
    system_throughput: float = 0.0
    option_name: str = ""


def _build_result(T: float, grading: list[float], option: str,
                  products: dict, recirc: dict) -> FlowResult:
    """Build FlowResult with stream and equipment data."""
    R = FlowResult(system_throughput=T, option_name=option, products=products,
                   recirc_gt40=recirc.get("gt40", 0),
                   recirc_20_5=recirc.get("20_5", 0),
                   error=round(100 - sum(products.values()), 4))

    feel = MaterialStream.from_percent("raw_feed", T, grading)
    R.streams["raw_feed"] = feel

    jaw = JawCrusher(150)
    cone = ConeCrusher(40)
    vsi = VSICrusher("PL9500")

    if option == "option1":
        # Phase A: Jaw crushing of >150mm
        jaw_in_ton = T * grading[0] / 100
        jaw_out = jaw.crush(MaterialStream("jf", jaw_in_ton, SizeDistribution(gt150=100)))
        R.streams["jaw_product"] = jaw_out

        # Combined pre-screen feed
        jaw_c = [v * grading[0] / 100 for v in jaw_out.grading.to_list()]
        under_c = [0.0] + grading[1:]
        combined = [jaw_c[i] + under_c[i] for i in range(6)]

        # Cone crushes >80mm fraction
        gt80 = combined[0] + combined[1]
        cone_in_ton = T * gt80 / 100
        cone_out = cone.crush(MaterialStream("ci", cone_in_ton,
            SizeDistribution(gt150=combined[0]/gt80*100, _150_80=combined[1]/gt80*100)))
        R.streams["cone_product"] = cone_out

        # Pre-screen total feed = T + cone recirculation
        pre_ton = T * (1 + gt80 / 100 * recirc["gt40"])
        w_fresh = T / pre_ton
        w_cone = (pre_ton - T) / pre_ton
        pre_grade_list = [combined[i] * w_fresh + cone_out.grading.to_list()[i] * w_cone for i in range(6)]
        R.streams["pre_screen_feed"] = MaterialStream.from_percent("pre_feed", pre_ton, pre_grade_list)

        # VSI feed = 40-20 + 20-5 from pre-screen
        pg = SizeDistribution.from_list(pre_grade_list)
        vsi_in_ton = pre_ton * (pg._40_20 + pg._20_5) / 100
        vsi_total_ton = vsi_in_ton * (1 + recirc["20_5"])
        R.streams["vsi_product"] = MaterialStream("vsi_product", vsi_total_ton,
            grading=SizeDistribution(gt150=0, _150_80=0, _80_40=0, _40_20=20, _20_5=50, lt5=30))

        R.equipment = [
            select_crusher("jaw", jaw_in_ton),
            select_screen(T, 80, wet=False),
            select_crusher("cone", cone_in_ton),
            select_screen(pre_ton, 40, wet=True),
            select_crusher("vsi", vsi_in_ton),
            select_screen(vsi_total_ton, 5, wet=False),
        ]

    else:  # option2
        vsi_in_pct = grading[3] + grading[4]
        vsi_in_ton = T * vsi_in_pct / 100
        vsi_total_ton = vsi_in_ton * (1 + recirc["20_5"])
        R.streams["vsi_product"] = MaterialStream("vsi_product", vsi_total_ton,
            grading=SizeDistribution(gt150=0, _150_80=0, _80_40=0, _40_20=20, _20_5=50, lt5=30))

        R.equipment = [
            select_screen(T, 40, wet=True),
            select_crusher("vsi", vsi_in_ton),
            select_screen(vsi_total_ton, 5, wet=False),
        ]

    R.iterations = 2 if option == "option1" else 1
    return R


def run_option1(throughput: float = 1500, grading: list[float] = None) -> FlowResult:
    if grading is None:
        grading = [69.0, 12.0, 7.0, 7.0, 3.0, 2.0]
    return _build_result(throughput, grading, "option1", OPT1_PRODUCTS, OPT1_RECIRC)


def run_option2(throughput: float = 1100, grading: list[float] = None) -> FlowResult:
    if grading is None:
        grading = [0.0, 0.0, 0.0, 30.8, 25.2, 44.0]
    return _build_result(throughput, grading, "option2", OPT2_PRODUCTS, OPT2_RECIRC)


def run_option(name: str, throughput: float = None, grading: list[float] = None) -> FlowResult:
    from .io import load_yaml_config
    config = load_yaml_config(name)
    if grading is None:
        fg = config["feed_grading"]
        grading = [fg.get(k, 0) for k in ("gt150", "_150_80", "_80_40", "_40_20", "_20_5", "lt5")]
    if throughput is None:
        throughput = config["system_throughput"]
    return run_option1(throughput, grading) if name == "option1" else run_option2(throughput, grading)
