from .models import MaterialStream, SizeDistribution


# Excel Sheet2 row 7: Jaw crusher e=150 product grading (with dust loss)
# Excel Sheet2 row 6: jaw crusher e=150 open-circuit product grading
# 14% remains >150mm (elongated particles bypass CSS), 10% dust loss recovered
JAW_E150_PRODUCT = SizeDistribution(gt150=14, _150_80=33, _80_40=25, _40_20=12, _20_5=10, lt5=6)

# Excel Sheet2 row 10: Cone crusher e=40 product grading
CONE_E40_PRODUCT = SizeDistribution(gt150=0, _150_80=0, _80_40=17, _40_20=28, _20_5=38, lt5=17)

# VSICrusher PL9500 product ratio (from Excel Sheet2 row 22)
VSI_PRODUCT_RATIO = (0.20, 0.50, 0.30)  # 40-20 : 20-5 : <5


class JawCrusher:
    """Jaw crusher model — coarse crushing, open circuit"""

    def __init__(self, closed_side_setting: float = 150):
        self.css = closed_side_setting

    def crush(self, feed: MaterialStream) -> MaterialStream:
        if self.css == 150:
            product_curve = JAW_E150_PRODUCT
        else:
            scale = self.css / 150.0
            base = JAW_E150_PRODUCT
            product_curve = SizeDistribution(
                gt150=0,
                _150_80=base._150_80 * (1 - scale * 0.3),
                _80_40=base._80_40 * (1 - scale * 0.1),
                _40_20=base._40_20 * (1 + scale * 0.1),
                _20_5=base._20_5 * (1 + scale * 0.2),
                lt5=base.lt5 * (1 + scale * 0.3),
            )
        return MaterialStream(
            name=f"{feed.name}_jaw_crushed",
            tonnage=feed.tonnage,
            grading=product_curve,
        )


class ConeCrusher:
    """Cone crusher model — medium crushing, closed circuit"""

    def __init__(self, closed_side_setting: float = 40):
        self.css = closed_side_setting

    def crush(self, feed: MaterialStream) -> MaterialStream:
        if self.css == 40:
            product_curve = CONE_E40_PRODUCT
        else:
            scale = self.css / 40.0
            base = CONE_E40_PRODUCT
            product_curve = SizeDistribution(
                gt150=0, _150_80=0,
                _80_40=base._80_40 * (1 + scale * 0.2),
                _40_20=base._40_20 * (1 - scale * 0.1),
                _20_5=base._20_5 * (1 - scale * 0.05),
                lt5=base.lt5 * (1 - scale * 0.05),
            )
        return MaterialStream(
            name=f"{feed.name}_cone_crushed",
            tonnage=feed.tonnage,
            grading=product_curve,
        )


class VSICrusher:
    """Vertical Shaft Impact crusher model — sand making, closed circuit"""

    def __init__(self, model: str = "PL9500"):
        self.model = model

    def crush(self, feed: MaterialStream) -> MaterialStream:
        r40, r20, r5 = VSI_PRODUCT_RATIO
        return MaterialStream(
            name=f"{feed.name}_vsi_crushed",
            tonnage=feed.tonnage,
            grading=SizeDistribution(
                gt150=0, _150_80=0, _80_40=0,
                _40_20=r40 * 100,
                _20_5=r20 * 100,
                lt5=r5 * 100,
            ),
        )
