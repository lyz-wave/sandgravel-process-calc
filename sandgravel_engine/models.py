from dataclasses import dataclass, field

SIZE_LABELS = ["gt150", "_150_80", "_80_40", "_40_20", "_20_5", "lt5"]


@dataclass
class SizeDistribution:
    gt150: float = 0.0
    _150_80: float = 0.0
    _80_40: float = 0.0
    _40_20: float = 0.0
    _20_5: float = 0.0
    lt5: float = 0.0

    def total(self) -> float:
        return self.gt150 + self._150_80 + self._80_40 + self._40_20 + self._20_5 + self.lt5

    def validate(self) -> bool:
        return abs(self.total() - 100.0) < 0.1

    def __add__(self, other: "SizeDistribution") -> "SizeDistribution":
        return SizeDistribution(
            gt150=self.gt150 + other.gt150,
            _150_80=self._150_80 + other._150_80,
            _80_40=self._80_40 + other._80_40,
            _40_20=self._40_20 + other._40_20,
            _20_5=self._20_5 + other._20_5,
            lt5=self.lt5 + other.lt5,
        )

    def __mul__(self, factor: float) -> "SizeDistribution":
        return SizeDistribution(
            gt150=self.gt150 * factor,
            _150_80=self._150_80 * factor,
            _80_40=self._80_40 * factor,
            _40_20=self._40_20 * factor,
            _20_5=self._20_5 * factor,
            lt5=self.lt5 * factor,
        )

    def __rmul__(self, factor: float) -> "SizeDistribution":
        return self.__mul__(factor)

    def to_list(self) -> list[float]:
        return [self.gt150, self._150_80, self._80_40, self._40_20, self._20_5, self.lt5]

    @classmethod
    def from_list(cls, values: list[float]) -> "SizeDistribution":
        if len(values) != len(SIZE_LABELS):
            raise ValueError(f"Expected {len(SIZE_LABELS)} values, got {len(values)}")
        return cls(*values)


@dataclass
class MaterialStream:
    name: str
    tonnage: float
    grading: SizeDistribution = field(default_factory=SizeDistribution)
    moisture: float = 0.0

    @classmethod
    def from_percent(cls, name: str, tonnage: float, percents: list[float]) -> "MaterialStream":
        return cls(name=name, tonnage=tonnage, grading=SizeDistribution.from_list(percents))

    def tonnage_by_size(self, size_index: int) -> float:
        return self.tonnage * self.grading.to_list()[size_index] / 100.0

    def tonnage_gt150(self) -> float:
        return self.tonnage * self.grading.gt150 / 100.0

    def tonnage_gt80(self) -> float:
        return self.tonnage * (self.grading.gt150 + self.grading._150_80) / 100.0

    def tonnage_gt40(self) -> float:
        return self.tonnage * (self.grading.gt150 + self.grading._150_80 + self.grading._80_40) / 100.0

    def tonnage_lt40(self) -> float:
        return self.tonnage * (self.grading._40_20 + self.grading._20_5 + self.grading.lt5) / 100.0

    def tonnage_lt5(self) -> float:
        return self.tonnage * self.grading.lt5 / 100.0

    def split(self, ratio: float) -> tuple["MaterialStream", "MaterialStream"]:
        part1_tonnage = self.tonnage * ratio
        part2_tonnage = self.tonnage * (1 - ratio)
        return (
            MaterialStream(name=f"{self.name}_a", tonnage=part1_tonnage, grading=self.grading),
            MaterialStream(name=f"{self.name}_b", tonnage=part2_tonnage, grading=self.grading),
        )


@dataclass
class EquipmentSelection:
    model: str
    quantity: int
    unit_capacity: float
    actual_throughput: float

    @property
    def load_factor(self) -> float:
        if self.quantity * self.unit_capacity == 0:
            return 0.0
        return self.actual_throughput / (self.quantity * self.unit_capacity)


@dataclass
class BalanceResult:
    streams: dict[str, MaterialStream]
    equipment: list[EquipmentSelection]
    iterations: int
    convergence_error: float

    def to_dict(self) -> dict:
        return {
            "streams": {k: {"tonnage": v.tonnage, "grading": v.grading.to_list()} for k, v in self.streams.items()},
            "equipment": [{"model": e.model, "quantity": e.quantity,
                          "unit_capacity": e.unit_capacity, "load_factor": e.load_factor} for e in self.equipment],
            "iterations": self.iterations,
            "convergence_error": self.convergence_error,
        }
