# 砂石加工系统工艺计算平台 — 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建砂石骨料加工系统工艺计算平台：Python计算引擎 + FastAPI后端 + React前端 + 设计说明书

**Architecture:** 三层分离 — sandgravel_engine(纯计算核心，零Web依赖) → backend(FastAPI薄层) → frontend(React SPA交互式可视化)

**Tech Stack:** Python 3.11+ (dataclasses, pytest, openpyxl, pyyaml), FastAPI + Pydantic, React 18 + Vite + TypeScript

---

## Phase 1: 项目脚手架 + 数据模型

### Task 1.1: 创建项目目录结构

**Files:**
- Create: `sandgravel_engine/__init__.py`
- Create: `sandgravel_engine/models.py`
- Create: `tests/__init__.py`
- Create: `tests/conftest.py`
- Create: `backend/__init__.py`
- Create: `sandgravel_engine/config/`

- [ ] **Step 1: 创建目录和空文件**

```bash
cd "C:/Users/Admin/Desktop/砂石系统"
mkdir -p sandgravel_engine/config
mkdir -p tests/fixtures
mkdir -p backend/api
mkdir -p frontend/src
```

- [ ] **Step 2: 验证目录结构**

```bash
ls -R sandgravel_engine/ tests/ backend/
```

Expected: 所有目录存在，`__init__.py` 文件已创建

### Task 1.2: 定义核心数据模型

**Files:**
- Create: `sandgravel_engine/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: 编写数据模型测试**

```python
# tests/test_models.py
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
    # >80mm = 10+20 = 30% of 1000 = 300
    assert abs(ms.tonnage_gt80() - 300) < 0.01
    # <40mm = 20+15+5 = 40% of 1000 = 400
    assert abs(ms.tonnage_lt40() - 400) < 0.01

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
```

- [ ] **Step 2: 运行测试确认失败**

```bash
cd "C:/Users/Admin/Desktop/砂石系统"
python -m pytest tests/test_models.py -v
```

Expected: FAIL — module not found

- [ ] **Step 3: 实现数据模型**

```python
# sandgravel_engine/models.py
from dataclasses import dataclass, field
from typing import Optional

SIZE_LABELS = ["gt150", "_150_80", "_80_40", "_40_20", "_20_5", "lt5"]

@dataclass
class SizeDistribution:
    """粒度分布，单位：%"""
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
        return cls(*values)


@dataclass
class MaterialStream:
    """物料流"""
    name: str
    tonnage: float  # t/h
    grading: SizeDistribution = field(default_factory=SizeDistribution)
    moisture: float = 0.0

    @classmethod
    def from_percent(cls, name: str, tonnage: float, percents: list[float]) -> "MaterialStream":
        return cls(name=name, tonnage=tonnage, grading=SizeDistribution.from_list(percents))

    def tonnage_by_size(self, size_index: int) -> float:
        """返回指定粒级的吨位 (t/h)"""
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
        """按比例分割物料流"""
        part1_tonnage = self.tonnage * ratio
        part2_tonnage = self.tonnage * (1 - ratio)
        return (
            MaterialStream(name=f"{self.name}_a", tonnage=part1_tonnage, grading=self.grading),
            MaterialStream(name=f"{self.name}_b", tonnage=part2_tonnage, grading=self.grading),
        )


@dataclass
class EquipmentSelection:
    """设备选型结果"""
    model: str
    quantity: int
    unit_capacity: float  # 单机能力 t/h
    actual_throughput: float  # 实际通过量 t/h

    @property
    def load_factor(self) -> float:
        if self.quantity * self.unit_capacity == 0:
            return 0.0
        return self.actual_throughput / (self.quantity * self.unit_capacity)


@dataclass
class BalanceResult:
    """物料平衡计算结果"""
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_models.py -v
```

Expected: 7 passed

---

## Phase 2: 物料平衡引擎 (核心)

### Task 2.1: 平衡引擎 — 开路计算

**Files:**
- Create: `sandgravel_engine/balance.py`
- Create: `tests/test_balance.py`

- [ ] **Step 1: 编写开路平衡测试**

```python
# tests/test_balance.py
import pytest
from sandgravel_engine.models import MaterialStream, SizeDistribution
from sandgravel_engine.balance import BalanceEngine, ProcessNode, FlowConfig

def make_option1_feed():
    """Excel Sheet2 原料级配 (69,12,7,7,3,2)"""
    return MaterialStream.from_percent(
        "raw_feed", 1500,
        [69.0, 12.0, 7.0, 7.0, 3.0, 2.0]
    )

def test_open_circuit_jaw_crusher():
    """粗碎颚破 e=150 开路：验证产品级配"""
    feed = make_option1_feed()
    oversize = MaterialStream(name="grizzly_oversize", tonnage=feed.tonnage * 0.69,
                              grading=SizeDistribution(gt150=100, _150_80=0, _80_40=0, _40_20=0, _20_5=0, lt5=0))
    
    from sandgravel_engine.crushing import JawCrusher
    crusher = JawCrusher(closed_side_setting=150)
    product = crusher.crush(oversize)
    
    # Excel Sheet2 第7行：e=150颚破产品级配 14,33,25,12,10,6
    expected = [14.0, 33.0, 25.0, 12.0, 10.0, 6.0]
    for i, (actual, exp) in enumerate(zip(product.grading.to_list(), expected)):
        assert abs(actual - exp) < 0.1, f"size[{i}]: {actual} != {exp}"

def test_balance_engine_open():
    """开路平衡：粗碎+预筛分，无循环"""
    engine = BalanceEngine()
    feed = MaterialStream.from_percent("feed", 1500, [69, 12, 7, 7, 3, 2])
    
    # 定义流程：颚破→筛分（无循环）
    result = engine.solve(feed, recirculation_config=None)
    
    assert result.iterations == 1
    assert abs(result.convergence_error) < 0.0001
    # 预筛分80mm：筛上物约100-70=30%，即约450t/h去中碎
    assert "pre_screen_oversize" in result.streams
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_balance.py -v
```

Expected: FAIL

- [ ] **Step 3: 实现开路平衡引擎**

```python
# sandgravel_engine/balance.py
from dataclasses import dataclass, field
from typing import Optional, Callable
from .models import MaterialStream, SizeDistribution, BalanceResult

@dataclass
class ProcessNode:
    """流程节点"""
    name: str
    node_type: str  # "crusher", "screen", "splitter", "sink"
    params: dict = field(default_factory=dict)

@dataclass
class FlowConfig:
    """流程配置"""
    nodes: list[ProcessNode]
    edges: list[tuple[str, str]]  # (from_node, to_node)
    recirculation_edges: list[tuple[str, str]] = field(default_factory=list)

class BalanceEngine:
    """物料平衡引擎"""
    
    def __init__(self, max_iterations: int = 100, tolerance: float = 1e-4):
        self.max_iterations = max_iterations
        self.tolerance = tolerance

    def solve(self, feed: MaterialStream, config: FlowConfig) -> BalanceResult:
        """执行物料平衡计算"""
        streams: dict[str, MaterialStream] = {"feed": feed}
        equipment = []
        iterations = 0
        prev_error = float("inf")
        
        # 初始化所有节点流为0
        for node in config.nodes:
            streams[node.name] = MaterialStream(name=node.name, tonnage=0.0)
        
        while iterations < self.max_iterations:
            # 沿边传递物料
            for from_node, to_node in config.edges:
                if from_node in streams and streams[from_node].tonnage > 0:
                    streams[to_node] = MaterialStream(
                        name=to_node,
                        tonnage=streams[to_node].tonnage + streams[from_node].tonnage,
                        grading=streams[from_node].grading
                    )
            
            # 处理循环边
            for from_node, to_node in config.recirculation_edges:
                if from_node in streams and streams[from_node].tonnage > 0:
                    # 将循环量加回目标节点
                    streams[to_node] = MaterialStream(
                        name=to_node,
                        tonnage=streams[to_node].tonnage + streams[from_node].tonnage,
                        grading=streams[from_node].grading
                    )
            
            # 检查收敛
            total_flow = sum(s.tonnage for s in streams.values())
            error = abs(total_flow - prev_error) if iterations > 0 else total_flow
            if error < self.tolerance:
                break
            
            prev_error = total_flow
            iterations += 1
        
        return BalanceResult(
            streams=streams,
            equipment=equipment,
            iterations=iterations + 1,
            convergence_error=error
        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_balance.py::test_balance_engine_open -v
```

Expected: PASS

### Task 2.2: 闭路循环迭代收敛 — >40mm碎石循环

- [ ] **Step 1: 编写闭路平衡测试（对照Excel Sheet2）**

```python
# 追加到 tests/test_balance.py

def test_closed_circuit_gt40mm():
    """>40mm碎石闭路循环：验证5次迭代后产率收敛"""
    from sandgravel_engine.crushing import JawCrusher, ConeCrusher
    from sandgravel_engine.screening import Screen
    
    feed = MaterialStream.from_percent("raw_feed", 1500, [69, 12, 7, 7, 3, 2])
    
    # 颚破 e=150 产品
    jaw = JawCrusher(closed_side_setting=150)
    jaw_product = jaw.crush(
        MaterialStream(name="jaw_feed", tonnage=feed.tonnage * 0.69,
                       grading=SizeDistribution(gt150=100))
    )
    
    # 颚破产品+筛下细料合并
    combined_grading = jaw_product.grading.to_list()  # [14, 33, 25, 12, 10, 6]
    combined_grading = [g * 0.69 for g in combined_grading]  # 占原料69%
    undersize_grading = [0, 0, 0, 7, 3, 2]  # 占原料31% (100-69)
    for i in range(6):
        combined_grading[i] += undersize_grading[i]
    
    assert abs(sum(combined_grading) - 100) < 0.1, f"sum={sum(combined_grading)}"
    
    # Excel Sheet2 第8行：累计级配 9.66, 34.77, 24.25, 15.28, 9.9, 6.14
    expected = [9.66, 34.77, 24.25, 15.28, 9.9, 6.14]
    for i, (actual, exp) in enumerate(zip(combined_grading, expected)):
        assert abs(actual - exp) < 0.2, f"size[{i}]: actual={actual:.2f} expected={exp}"

def test_recirculation_convergence():
    """验证闭路循环迭代收敛到Excel结果"""
    from sandgravel_engine.crushing import ConeCrusher
    from sandgravel_engine.screening import Screen
    
    # Excel Sheet2 第8行：进入预筛分的物料级配
    feed_grading = SizeDistribution(gt150=9.66, _150_80=34.77, _80_40=24.25,
                                     _40_20=15.28, _20_5=9.9, lt5=6.14)
    feed = MaterialStream(name="pre_screen_feed", tonnage=1500, grading=feed_grading)
    
    cone = ConeCrusher(closed_side_setting=40)
    screen = Screen(aperture=80)
    
    # 闭路循环：预筛分>80mm → 中碎e=40 → 返回预筛分
    # 迭代至收敛
    oversize_gt80 = screen.oversize(feed)  # >80mm 部分 = 9.66+34.77=44.43%
    
    assert abs(oversize_gt80.tonnage / feed.tonnage * 100 - 44.43) < 0.2
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_balance.py::test_recirculation_convergence -v
```

Expected: FAIL (Screen class not defined yet)

- [ ] **Step 3: 实现闭路循环收敛算法**

```python
# 追加到 sandgravel_engine/balance.py

class RecirculationSolver:
    """闭路循环迭代求解器"""
    
    def __init__(self, max_iter: int = 100, tol: float = 1e-4):
        self.max_iter = max_iter
        self.tol = tol

    def solve(self, initial_feed: MaterialStream,
              process_fn: Callable[[MaterialStream], MaterialStream],
              recirc_fn: Callable[[MaterialStream], MaterialStream],
              recirc_ratio_fn: Callable[[MaterialStream], float]) -> BalanceResult:
        """
        闭路循环迭代求解
        
        Args:
            initial_feed: 初始给料
            process_fn: 主流程处理函数 (物料 → 产品物料)
            recirc_fn: 循环物料处理函数
            recirc_ratio_fn: 返回需要循环的比例
        
        Returns:
            BalanceResult with converged streams
        """
        current_feed = initial_feed
        total_recirc = MaterialStream(name="recirc_total", tonnage=0)
        streams = {}
        prev_tonnage = current_feed.tonnage
        
        for i in range(self.max_iter):
            # 处理当前给料
            product = process_fn(current_feed)
            
            # 计算循环量
            recirc_ratio = recirc_ratio_fn(product)
            recirc = MaterialStream(
                name=f"recirc_{i}",
                tonnage=product.tonnage * recirc_ratio,
                grading=product.grading
            )
            
            recirc_processed = recirc_fn(recirc)
            
            # 更新给料 = 原始给料 + 处理后循环料
            next_feed = MaterialStream(
                name=f"feed_iter_{i}",
                tonnage=initial_feed.tonnage + recirc_processed.tonnage,
                grading=SizeDistribution()  # 需要混合
            )
            
            # 收敛检查
            error = abs(next_feed.tonnage - prev_tonnage)
            if error < self.tol:
                streams["feed"] = next_feed
                streams["product"] = product
                streams["recirc"] = recirc
                return BalanceResult(
                    streams=streams, equipment=[],
                    iterations=i + 1, convergence_error=error
                )
            
            current_feed = next_feed
            prev_tonnage = next_feed.tonnage
            total_recirc.tonnage += recirc.tonnage
        
        raise ConvergenceError(f"未能在{self.max_iter}次内收敛，当前误差={error:.6f}")


class ConvergenceError(Exception):
    """平衡计算不收敛"""
    pass
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_balance.py -v
```

Expected: 3 passed

---

## Phase 3: 破碎产率模型

### Task 3.1: 颚式破碎机 (e=150)

**Files:**
- Create: `sandgravel_engine/crushing.py`
- Create: `tests/test_crushing.py`

- [ ] **Step 1: 编写颚破测试**

```python
# tests/test_crushing.py
import pytest
from sandgravel_engine.models import MaterialStream, SizeDistribution
from sandgravel_engine.crushing import JawCrusher

def test_jaw_crusher_e150_product():
    """Excel Sheet2 第7行：e=150颚破产品级配 14,33,25,12,10,6"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1035, SizeDistribution(gt150=100))  # 1500*0.69
    
    product = crusher.crush(feed)
    expected = [14, 33, 25, 12, 10, 6]
    
    for i, (actual, exp) in enumerate(zip(product.grading.to_list(), expected)):
        assert abs(actual - exp) < 0.1, f"size[{i}] actual={actual} expected={exp}"

def test_jaw_crusher_total_mass_conservation():
    """质量守恒：产品总量 = 给料总量"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1000, SizeDistribution(gt150=80, _150_80=20))
    product = crusher.crush(feed)
    assert abs(product.tonnage - 1000) < 0.01

def test_jaw_crusher_reduction_ratio():
    """破碎比：排矿口150mm，>150mm应全部破碎"""
    crusher = JawCrusher(closed_side_setting=150)
    feed = MaterialStream("feed", 1000, SizeDistribution(gt150=100))
    product = crusher.crush(feed)
    assert product.grading.gt150 == 0, "颚破产品不应含>150mm"
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_crushing.py -v
```

Expected: FAIL

- [ ] **Step 3: 实现颚破模型**

```python
# sandgravel_engine/crushing.py
from .models import MaterialStream, SizeDistribution

# 颚破 e=150 产品级配矩阵（来自Excel Sheet2 第6-7行）
# 给料级配 → 产品级配
JAW_E150_PRODUCT = SizeDistribution(
    gt150=0,    # >150mm 全部破碎
    _150_80=14, # 14% 进入150-80
    _80_40=33,  # 33% 进入80-40
    _40_20=25,  # 25% 进入40-20
    _20_5=12,   # 12% 进入20-5
    lt5=10,     # 10% 进入<5 (考虑粉尘损失，实际6%成品)
)

# Excel 第6行修正：考虑6%粉尘损失
JAW_E150_WITH_DUST = SizeDistribution(
    gt150=0, _150_80=14, _80_40=33, _40_20=25, _20_5=12, lt5=6
)
JAW_DUST_LOSS = 10 - 6  # 4% dust loss


class JawCrusher:
    """颚式破碎机模型"""

    def __init__(self, closed_side_setting: float = 150):
        self.css = closed_side_setting  # 排矿口 mm
        if self.css == 150:
            self.product_curve = JAW_E150_PRODUCT
        else:
            # 通用模型：按CSS比例缩放产品曲线
            self.product_curve = self._scale_curve(self.css)

    def _scale_curve(self, css: float) -> SizeDistribution:
        """根据排矿口缩放产品级配曲线"""
        scale = css / 150.0
        base = JAW_E150_PRODUCT
        # CSS越小，细粒级越多
        return SizeDistribution(
            gt150=0,
            _150_80=base._150_80 * (1 - scale * 0.3),
            _80_40=base._80_40 * (1 - scale * 0.1),
            _40_20=base._40_20 * (1 + scale * 0.1),
            _20_5=base._20_5 * (1 + scale * 0.2),
            lt5=base.lt5 * (1 + scale * 0.3),
        )

    def crush(self, feed: MaterialStream) -> MaterialStream:
        """破碎计算"""
        # 质量守恒
        return MaterialStream(
            name=f"{feed.name}_jaw_crushed",
            tonnage=feed.tonnage,
            grading=self.product_curve,
        )


class ConeCrusher:
    """圆锥破碎机模型"""

    def __init__(self, closed_side_setting: float = 40):
        self.css = closed_side_setting
        # Excel Sheet2 第10行：e=40圆锥破产品级配 17,28,38,17
        # >40mm = 17+28 = 45%, <40mm = 38+17 = 55%
        self.product_curve = SizeDistribution(
            gt150=0,
            _150_80=0,   # 圆锥破不出>80mm
            _80_40=17,   # 17% 仍>40mm（循环回去）
            _40_20=28,   # 28% 进入40-20
            _20_5=38,    # 38% 进入20-5
            lt5=17,      # 17% 进入<5
        )

    def crush(self, feed: MaterialStream) -> MaterialStream:
        return MaterialStream(
            name=f"{feed.name}_cone_crushed",
            tonnage=feed.tonnage,
            grading=self.product_curve,
        )


class VSICrusher:
    """立轴冲击式破碎机（制砂）模型"""

    def __init__(self, model: str = "PL9500"):
        self.model = model
        # Excel Sheet2 第22行：PL9500 产品比例 20:50:30
        # 40-20 : 20-5 : <5
        self.product_ratio = (0.20, 0.50, 0.30)

    def crush(self, feed: MaterialStream) -> MaterialStream:
        """制砂破碎：给料中40-20和20-5被破碎"""
        r40, r20, r5 = self.product_ratio
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
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_crushing.py -v
```

Expected: 3 passed

---

## Phase 4: 筛分模型（BEDVHTKPWSM 11因子）

### Task 4.1: 筛分计算核心

**Files:**
- Create: `sandgravel_engine/screening.py`
- Create: `tests/test_screening.py`

- [ ] **Step 1: 编写筛分测试（对照Excel Sheet4）**

```python
# tests/test_screening.py
import pytest
from sandgravel_engine.screening import ScreenCalculator, ScreenParams, ScreenResult

def test_screen_pre_screening_80mm_dry():
    """预筛分80mm干法：Excel Sheet4 第53-73行"""
    params = ScreenParams(
        aperture=80,          # 筛孔 mm
        wet=False,            # 干法
        basic_capacity=102,   # B: 基础筛分能力 t/m²·h
        efficiency_factor=1.0, # E: 效率修正
        deck_factor=0.9,      # D: 上层筛面
        oversize_factor=1.1,  # V: 筛上物含量修正
        undersize_factor=0.8, # H: 筛下物含量修正
        aperture_factor=1.0,  # T: 筛孔修正
        condition_factor=1.0, # K: 物料状态
        shape_factor=0.85,   # P: 颗粒形状
        moisture_factor=1.0,  # W: 水分
        safety_factor=1.28,   # S: 安全系数
        wet_factor=1.0,       # M: 湿筛修正 (干法=1)
    )
    
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=6.0)
    
    # Excel: Q = 87.893, 面积 = 14.4, 处理量 = 1265.66, 台数=2, 负荷=0.593
    assert abs(result.unit_capacity - 87.893) < 0.1
    assert abs(result.area - 14.4) < 0.1
    assert abs(result.capacity_per_unit - 1265.66) < 1
    assert result.num_units == 2
    assert abs(result.load_factor - 0.593) < 0.01

def test_screen_first_screening_40mm_wet():
    """第一筛分40mm湿法：Excel Sheet4 第98-118行"""
    params = ScreenParams(
        aperture=40, wet=True,
        basic_capacity=65,
        efficiency_factor=0.85,
        deck_factor=0.9,
        oversize_factor=1.03,
        undersize_factor=1.0,
        aperture_factor=1.0,
        condition_factor=1.0,
        shape_factor=0.9,
        moisture_factor=1.0,
        safety_factor=1.18,
        wet_factor=1.0,  # 湿筛时水分修正
    )
    
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5)
    
    # Excel: Q = 54.392, 面积 = 18, 处理量 = 979.06, 台数=4, 负荷=0.419
    assert abs(result.unit_capacity - 54.392) < 0.1
    assert abs(result.area - 18.0) < 0.1
    assert abs(result.capacity_per_unit - 979.06) < 1
    assert result.num_units == 4
    assert abs(result.load_factor - 0.419) < 0.01

def test_screen_second_screening_5mm_dry():
    """第二筛分5mm干法：Excel Sheet4 第164-187行"""
    params = ScreenParams(
        aperture=5, wet=False,
        basic_capacity=18,
        efficiency_factor=1.0,
        deck_factor=0.9,
        oversize_factor=1.4,
        undersize_factor=0.5,
        aperture_factor=1.0,
        condition_factor=0.9,
        shape_factor=0.95,
        moisture_factor=1.0,
        safety_factor=0.67,
        wet_factor=1.0,
    )
    
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5)
    
    # Excel: Q = 6.496, 面积 = 18, 处理量 = 116.93, 台数=6, 负荷=1.539
    assert abs(result.unit_capacity - 6.496) < 0.01
    assert abs(result.area - 18.0) < 0.1
    assert abs(result.capacity_per_unit - 116.93) < 0.1
    assert result.num_units == 6
    assert abs(result.load_factor - 1.539) < 0.01

def test_screen_5mm_wet():
    """第一筛分5mm湿法：Excel Sheet4 第142-162行"""
    params = ScreenParams(
        aperture=5, wet=True,
        basic_capacity=18,
        efficiency_factor=0.85,
        deck_factor=0.7,
        oversize_factor=1.42,
        undersize_factor=0.55,
        aperture_factor=1.2,
        condition_factor=1.0,
        shape_factor=0.95,
        moisture_factor=1.0,
        safety_factor=0.67,
        wet_factor=1.9,  # 湿筛修正
    )
    
    calc = ScreenCalculator()
    result = calc.calculate(params, screen_width=2.4, screen_length=7.5)
    
    assert abs(result.unit_capacity - 12.139) < 0.01
    assert result.num_units == 4
    assert abs(result.load_factor - 0.789) < 0.01
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_screening.py -v
```

Expected: FAIL

- [ ] **Step 3: 实现筛分计算**

```python
# sandgravel_engine/screening.py
from dataclasses import dataclass

@dataclass
class ScreenParams:
    """筛分计算输入参数"""
    aperture: float          # 筛孔尺寸 mm
    wet: bool                # 是否湿法
    basic_capacity: float    # B: 基础筛分能力 t/m²·h
    efficiency_factor: float # E: 筛分效率修正
    deck_factor: float       # D: 筛面层位修正
    oversize_factor: float   # V: 筛上物含量修正
    undersize_factor: float  # H: 筛下物含量修正
    aperture_factor: float   # T: 筛孔尺寸修正
    condition_factor: float  # K: 物料状态修正
    shape_factor: float      # P: 颗粒形状修正
    moisture_factor: float   # W: 水分修正
    safety_factor: float     # S: 安全系数
    wet_factor: float        # M: 湿筛修正 (干法=1.0)


@dataclass
class ScreenResult:
    """筛分计算结果"""
    unit_capacity: float     # Q: 单位面积处理能力 t/m²·h
    area: float              # 所需筛分面积 m²
    capacity_per_unit: float # 单台处理量 t/h
    num_units: int           # 所需台数
    load_factor: float       # 负荷率
    required_throughput: float  # 要求处理量 t/h


class ScreenCalculator:
    """振动筛分设备选型计算器
    Q = B × E × D × V × H × T × K × P × W × S × M
    """

    def calculate(self, params: ScreenParams, screen_width: float,
                  screen_length: float, required_throughput: float = None) -> ScreenResult:
        # Q = B × E × D × V × H × T × K × P × W × S × M
        Q = (
            params.basic_capacity *
            params.efficiency_factor *
            params.deck_factor *
            params.oversize_factor *
            params.undersize_factor *
            params.aperture_factor *
            params.condition_factor *
            params.shape_factor *
            params.moisture_factor *
            params.safety_factor *
            params.wet_factor
        )

        area_per_unit = screen_width * screen_length  # m²
        capacity_per_unit = area_per_unit * Q  # t/h per unit

        if required_throughput is None:
            num_units = 1
        else:
            num_units = max(1, int(required_throughput / capacity_per_unit) + 
                           (1 if required_throughput % capacity_per_unit > 0 else 0))

        actual_total_capacity = num_units * capacity_per_unit
        load_factor = required_throughput / actual_total_capacity if required_throughput else 1.0

        return ScreenResult(
            unit_capacity=Q,
            area=area_per_unit,
            capacity_per_unit=capacity_per_unit,
            num_units=num_units,
            load_factor=load_factor,
            required_throughput=required_throughput or capacity_per_unit,
        )
```

- [ ] **Step 4: 运行测试确认通过**

```bash
python -m pytest tests/test_screening.py -v
```

Expected: 4 passed

---

## Phase 5: 设备选型 + 流程编排

### Task 5.1: 设备库 + 选型逻辑

**Files:**
- Create: `sandgravel_engine/equipment.py`
- Create: `tests/test_equipment.py`

- [ ] **Step 1: 编写设备选型测试**

```python
# tests/test_equipment.py
import pytest
from sandgravel_engine.equipment import EquipmentDB, select_crusher, select_screen

def test_equipment_db_has_jaw_crushers():
    db = EquipmentDB()
    jaw_crushers = db.get_by_type("jaw_crusher")
    assert len(jaw_crushers) > 0
    assert any(c.model == "Ci125" for c in jaw_crushers)

def test_select_jaw_crusher_1200tph():
    """Excel Sheet2 第56行：1200T/H 选3台Ci125"""
    result = select_crusher("jaw", 1200)
    assert result.model == "Ci125"
    assert result.quantity == 3
    assert abs(result.load_factor - 0.8) < 0.01

def test_select_cone_crusher_817tph():
    """Excel Sheet2 第58行：817T/H 选3台Ci225"""
    result = select_crusher("cone", 817)
    assert result.model == "Ci225"
    assert result.quantity == 3
    assert abs(result.load_factor - 0.65) < 0.01

def test_select_vsi_1080tph():
    """Excel Sheet2 第60行：1080T/H 选6台PL9500"""
    result = select_crusher("vsi", 1080)
    assert result.model == "PL9500"
    assert result.quantity == 6

def test_select_screen_1640tph():
    """Excel Sheet2 第59行：1640T/H 选4台3YKR2472"""
    result = select_screen(1640, aperture=40, wet=True)
    assert result.quantity == 4
```

- [ ] **Step 2: 运行测试确认失败**

```bash
python -m pytest tests/test_equipment.py -v
```

Expected: FAIL

- [ ] **Step 3: 实现设备选型**

```python
# sandgravel_engine/equipment.py
from dataclasses import dataclass
from typing import Optional
from .models import EquipmentSelection


@dataclass
class EquipmentSpec:
    """设备规格"""
    model: str
    eq_type: str  # "jaw_crusher", "cone_crusher", "vsi", "screen", "sand_recovery"
    unit_capacity: float  # t/h
    screen_area: Optional[float] = None  # m² (仅筛分机)
    screen_layers: Optional[int] = None  # 筛面层数
    max_feed_size: Optional[float] = None  # 最大给料粒度 mm
    power: Optional[float] = None  # kW


# 设备数据库（来自Excel源文件）
_DEFAULT_EQUIPMENT = [
    EquipmentSpec("Ci125", "jaw_crusher", 500, max_feed_size=800, power=160),
    EquipmentSpec("Ci225", "cone_crusher", 420, max_feed_size=250, power=220),
    EquipmentSpec("PL9500", "vsi", 180, max_feed_size=40, power=2*250),
    EquipmentSpec("PL8500", "sand_recovery", 95, max_feed_size=5, power=2*132),
    EquipmentSpec("2YKR3060", "screen", 0, screen_area=18, screen_layers=2),
    EquipmentSpec("3YKR2472", "screen", 0, screen_area=18, screen_layers=3),
    EquipmentSpec("2YKR2472", "screen", 0, screen_area=18, screen_layers=2),
]


class EquipmentDB:
    """设备数据库"""

    def __init__(self, equipment: list[EquipmentSpec] = None):
        self._equipment = equipment or _DEFAULT_EQUIPMENT

    def get_by_type(self, eq_type: str) -> list[EquipmentSpec]:
        return [e for e in self._equipment if e.eq_type == eq_type]

    def get_by_model(self, model: str) -> Optional[EquipmentSpec]:
        for e in self._equipment:
            if e.model == model:
                return e
        return None


def select_crusher(crusher_type: str, required_throughput: float,
                   db: EquipmentDB = None) -> EquipmentSelection:
    """选择破碎机型号和台数"""
    if db is None:
        db = EquipmentDB()
    
    type_map = {"jaw": "jaw_crusher", "cone": "cone_crusher", "vsi": "vsi"}
    eq_type = type_map.get(crusher_type, crusher_type)
    candidates = sorted(db.get_by_type(eq_type), key=lambda e: e.unit_capacity, reverse=True)
    
    if not candidates:
        raise ValueError(f"无可用{crusher_type}破碎机")
    
    best = candidates[0]  # 选最大型号
    num_units = max(1, int(required_throughput / best.unit_capacity) + 
                   (1 if required_throughput % best.unit_capacity > 0 else 0))
    
    return EquipmentSelection(
        model=best.model,
        quantity=num_units,
        unit_capacity=best.unit_capacity,
        actual_throughput=required_throughput,
    )


def select_screen(required_throughput: float, aperture: float, wet: bool = False,
                  db: EquipmentDB = None) -> EquipmentSelection:
    """选择筛分机型号和台数"""
    if db is None:
        db = EquipmentDB()
    
    from .screening import ScreenCalculator, ScreenParams
    
    # 根据筛孔确定筛分参数（查阅Excel Sheet4）
    if aperture >= 60:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=80,
            efficiency_factor=1.0, deck_factor=0.9, oversize_factor=1.1, undersize_factor=0.5,
            aperture_factor=0.8, condition_factor=1.0, shape_factor=0.85, moisture_factor=1.0,
            safety_factor=1.28, wet_factor=1.0)
    elif aperture >= 40:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=65,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.9 if wet else 0.8,
            oversize_factor=1.03 if wet else 1.1, undersize_factor=1.0 if wet else 0.75,
            aperture_factor=1.0, condition_factor=1.0, shape_factor=0.9, moisture_factor=1.0,
            safety_factor=1.18, wet_factor=1.0 if wet else 1.0)
    elif aperture >= 20:
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=48,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.8, oversize_factor=1.08 if wet else 1.4,
            undersize_factor=0.8 if wet else 0.6, aperture_factor=1.0, condition_factor=1.0,
            shape_factor=0.9, moisture_factor=1.0, safety_factor=0.99 if wet else 1.28,
            wet_factor=1.0)
    else:  # 5mm or smaller
        params = ScreenParams(aperture=aperture, wet=wet, basic_capacity=18,
            efficiency_factor=0.85 if wet else 1.0, deck_factor=0.7 if wet else 0.9,
            oversize_factor=1.42 if wet else 1.4, undersize_factor=0.55 if wet else 0.5,
            aperture_factor=1.2 if wet else 1.0, condition_factor=1.0, shape_factor=0.95,
            moisture_factor=1.0, safety_factor=0.67, wet_factor=1.9 if wet else 1.0)
    
    calc = ScreenCalculator()
    # 根据筛孔选择筛面尺寸
    if aperture >= 40:
        width, length = 2.4, 6.0
    else:
        width, length = 2.4, 7.5
    
    result = calc.calculate(params, width, length, required_throughput)
    
    # 选择筛分机型号
    if aperture >= 40:
        model = "2YKR3060" if aperture >= 60 else "2YKR3060"
    elif aperture >= 20:
        model = "3YKR2472"
    else:
        model = "2YKR2472"
    
    return EquipmentSelection(
        model=model,
        quantity=result.num_units,
        unit_capacity=result.capacity_per_unit,
        actual_throughput=required_throughput,
    )
```

- [ ] **Step 4: 运行测试**

```bash
python -m pytest tests/test_equipment.py -v
```

---

## Phase 6: IO模块 + 配置文件

### Task 6.1: YAML配置 + Excel导入导出

**Files:**
- Create: `sandgravel_engine/io.py`
- Create: `sandgravel_engine/config/option1.yaml`
- Create: `sandgravel_engine/config/option2.yaml`
- Create: `tests/test_io.py`

- [ ] **Step 1: 编写IO测试**

```python
# tests/test_io.py
import pytest
import tempfile
import os
from sandgravel_engine.io import load_yaml_config, export_to_excel, import_from_excel
from sandgravel_engine.models import BalanceResult, MaterialStream, SizeDistribution, EquipmentSelection

def test_load_option1_yaml():
    config = load_yaml_config("option1")
    assert config["system_throughput"] == 1500
    assert abs(config["feed_grading"]["gt150"] - 69.0) < 0.01
    assert config["jaw_crusher"]["css"] == 150

def test_export_import_roundtrip():
    """Excel导出再导入，数据不变"""
    sd = SizeDistribution(gt150=9.66, _150_80=34.77, _80_40=24.25, _40_20=15.28, _20_5=9.9, lt5=6.14)
    ms = MaterialStream(name="test", tonnage=1500, grading=sd)
    eq = [EquipmentSelection("Ci125", 3, 500, 1200)]
    br = BalanceResult(streams={"feed": ms}, equipment=eq, iterations=5, convergence_error=0.00001)
    
    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
        path = f.name
    
    try:
        export_to_excel(br, path)
        assert os.path.exists(path)
        imported = import_from_excel(path)
        assert "feed" in imported.streams
    finally:
        os.unlink(path)
```

- [ ] **Step 2: 创建配置文件**

```yaml
# sandgravel_engine/config/option1.yaml
system_throughput: 1500
design_throughput: 1200
feed_grading:
  gt150: 69.0
  _150_80: 12.0
  _80_40: 7.0
  _40_20: 7.0
  _20_5: 3.0
  lt5: 2.0
jaw_crusher:
  model: Ci125
  css: 150
  quantity: 3
  unit_capacity: 500
cone_crusher:
  model: Ci225
  css: 40
  quantity: 3
  unit_capacity: 420
vsi_crusher:
  model: PL9500
  quantity: 6
sand_recovery:
  model: PL8500
  quantity: 2
screens:
  pre_screening:
    model: 2YKR3060
    aperture: 80
    quantity: 3
  first_screening:
    model: 3YKR2472
    apertures: [40, 20, 5]
    quantity: 4
    wet: true
  second_screening:
    model: 2YKR2472
    aperture: 5
    quantity: 6
```

```yaml
# sandgravel_engine/config/option2.yaml
system_throughput: 1100
design_throughput: 880
feed_grading:
  _40_20: 30.8
  _20_5: 25.2
  lt5: 44.0
  gt150: 0
  _150_80: 0
  _80_40: 0
jaw_crusher:
  model: Ci125
  css: 150
  quantity: 3
  unit_capacity: 500
cone_crusher:
  model: Ci225
  css: 40
  quantity: 3
  unit_capacity: 420
vsi_crusher:
  model: PL9500
  quantity: 6
screens:
  pre_screening:
    model: 2YKR3060
    aperture: 80
    quantity: 3
  first_screening:
    model: 3YKR2472
    apertures: [40, 20, 5]
    quantity: 4
    wet: true
  second_screening:
    model: 2YKR2472
    aperture: 5
    quantity: 6
```

- [ ] **Step 3: 实现IO模块**

```python
# sandgravel_engine/io.py
import yaml
import json
import os
from pathlib import Path
from typing import Optional
from .models import BalanceResult, MaterialStream, SizeDistribution, EquipmentSelection

_CONFIG_DIR = Path(__file__).parent / "config"


def load_yaml_config(option_name: str) -> dict:
    """加载YAML配置文件"""
    path = _CONFIG_DIR / f"{option_name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def export_to_excel(result: BalanceResult, path: str):
    """导出平衡计算结果到Excel"""
    import openpyxl
    wb = openpyxl.Workbook()
    
    # Sheet1: 物料流
    ws1 = wb.active
    ws1.title = "物料平衡"
    ws1.append(["名称", "吨位(t/h)", ">150", "150-80", "80-40", "40-20", "20-5", "<5"])
    for name, stream in result.streams.items():
        ws1.append([name, stream.tonnage] + stream.grading.to_list())
    
    # Sheet2: 设备选型
    ws2 = wb.create_sheet("设备选型")
    ws2.append(["型号", "台数", "单机能力(t/h)", "负荷率"])
    for eq in result.equipment:
        ws2.append([eq.model, eq.quantity, eq.unit_capacity, eq.load_factor])
    
    wb.save(path)


def import_from_excel(path: str) -> BalanceResult:
    """从Excel导入平衡计算结果"""
    import openpyxl
    wb = openpyxl.load_workbook(path, data_only=True)
    
    streams = {}
    ws1 = wb["物料平衡"]
    for row in ws1.iter_rows(min_row=2, values_only=True):
        name, tonnage, *grading_values = row
        sd = SizeDistribution.from_list(list(grading_values))
        streams[name] = MaterialStream(name=name, tonnage=tonnage, grading=sd)
    
    equipment = []
    if "设备选型" in wb.sheetnames:
        ws2 = wb["设备选型"]
        for row in ws2.iter_rows(min_row=2, values_only=True):
            model, qty, unit_cap, load = row
            equipment.append(EquipmentSelection(
                model=model, quantity=int(qty), unit_capacity=unit_cap,
                actual_throughput=unit_cap * qty * load if load else 0
            ))
    
    return BalanceResult(streams=streams, equipment=equipment, iterations=0, convergence_error=0)


def export_to_json(result: BalanceResult) -> str:
    """导出为JSON字符串"""
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=2)
```

---

## Phase 7: FastAPI 后端

### Task 7.1: API 端点

**Files:**
- Create: `backend/app.py`
- Create: `backend/models.py`
- Create: `backend/api/__init__.py`
- Create: `backend/api/balance.py`
- Create: `backend/api/equipment.py`
- Create: `backend/api/screening.py`
- Create: `backend/api/io.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: 编写API测试**

```python
# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.insert(0, "C:/Users/Admin/Desktop/砂石系统")
from backend.app import app

client = TestClient(app)

def test_get_options():
    response = client.get("/api/options")
    assert response.status_code == 200
    data = response.json()
    assert "configs" in data

def test_balance_calculate_option1():
    response = client.post("/api/balance/calculate", json={"config_name": "option1"})
    assert response.status_code == 200
    data = response.json()
    assert "streams" in data
    assert data["iterations"] > 0
    assert data["convergence_error"] < 0.001

def test_balance_validate_grading():
    """级配之和≠100%应拒绝"""
    bad_config = {
        "config_name": "custom",
        "feed_grading": [50, 20, 10, 5, 5, 5],  # sum=95
        "system_throughput": 1500,
    }
    response = client.post("/api/balance/calculate", json=bad_config)
    assert response.status_code == 422
```

- [ ] **Step 2: 实现FastAPI后端**

```python
# backend/app.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="砂石加工系统工艺计算平台", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

from backend.api import balance, equipment, screening, io

app.include_router(balance.router, prefix="/api")
app.include_router(equipment.router, prefix="/api")
app.include_router(screening.router, prefix="/api")
app.include_router(io.router, prefix="/api")


@app.get("/api/options")
async def get_options():
    from sandgravel_engine.io import load_yaml_config
    return {
        "configs": ["option1", "option2"],
        "equipment_types": ["jaw_crusher", "cone_crusher", "vsi", "screen", "sand_recovery"],
    }
```

```python
# backend/api/balance.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional
from sandgravel_engine.models import MaterialStream, SizeDistribution
from sandgravel_engine.balance import BalanceEngine, FlowConfig, ProcessNode

router = APIRouter()


class BalanceRequest(BaseModel):
    config_name: Optional[str] = "option1"
    feed_grading: Optional[list[float]] = None
    system_throughput: Optional[float] = None

    @field_validator("feed_grading")
    @classmethod
    def check_grading_sum(cls, v):
        if v is not None:
            total = sum(v)
            if abs(total - 100.0) > 0.1:
                raise ValueError(f"级配之和必须为100%，当前={total}%")
        return v


@router.post("/balance/calculate")
async def calculate_balance(req: BalanceRequest):
    from sandgravel_engine.io import load_yaml_config
    
    config = load_yaml_config(req.config_name)
    
    if req.feed_grading:
        grading = SizeDistribution.from_list(req.feed_grading)
    else:
        fg = config["feed_grading"]
        grading = SizeDistribution(**{k: fg.get(k, 0) for k in SizeDistribution.__dataclass_fields__})
    
    throughput = req.system_throughput or config["system_throughput"]
    feed = MaterialStream(name="raw_feed", tonnage=throughput, grading=grading)
    
    # 构建流程
    nodes = [
        ProcessNode("grizzly", "screen", {"aperture": 150}),
        ProcessNode("jaw_crusher", "crusher", {"css": 150}),
        ProcessNode("pre_screen", "screen", {"aperture": 80}),
        ProcessNode("cone_crusher", "crusher", {"css": 40}),
        ProcessNode("first_screen", "screen", {"apertures": [40, 20, 5]}),
        ProcessNode("vsi_crusher", "crusher", {"type": "vsi"}),
        ProcessNode("second_screen", "screen", {"aperture": 5}),
    ]
    edges = [
        ("raw_feed", "grizzly"),
        ("grizzly_oversize", "jaw_crusher"),
        ("jaw_crusher", "pre_screen"),
        ("grizzly_undersize", "pre_screen"),
        ("pre_screen_oversize", "cone_crusher"),
        ("cone_crusher", "pre_screen"),
        ("pre_screen_undersize", "first_screen"),
        ("first_screen_40_20", "vsi_crusher"),
        ("first_screen_20_5", "vsi_crusher"),
        ("vsi_crusher", "second_screen"),
        ("second_screen_oversize", "vsi_crusher"),
    ]
    
    flow = FlowConfig(nodes=nodes, edges=edges)
    engine = BalanceEngine()
    
    try:
        result = engine.solve(feed, flow)
        return result.to_dict()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

```python
# backend/api/equipment.py
from fastapi import APIRouter

router = APIRouter()

@router.post("/equipment/select")
async def select_equipment(req: dict):
    from sandgravel_engine.equipment import select_crusher, select_screen
    eq_type = req.get("type")
    throughput = req.get("throughput")
    
    if eq_type in ("jaw", "cone", "vsi"):
        result = select_crusher(eq_type, throughput)
    elif eq_type == "screen":
        result = select_screen(throughput, req.get("aperture", 40), req.get("wet", False))
    else:
        return {"error": f"Unknown equipment type: {eq_type}"}
    
    return {"model": result.model, "quantity": result.quantity,
            "unit_capacity": result.unit_capacity, "load_factor": result.load_factor}
```

```python
# backend/api/screening.py
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ScreenCalcRequest(BaseModel):
    aperture: float
    wet: bool = False
    basic_capacity: float
    efficiency_factor: float = 1.0
    deck_factor: float = 0.9
    oversize_factor: float = 1.1
    undersize_factor: float = 0.8
    aperture_factor: float = 1.0
    condition_factor: float = 1.0
    shape_factor: float = 0.85
    moisture_factor: float = 1.0
    safety_factor: float = 1.28
    wet_factor: float = 1.0
    screen_width: float = 2.4
    screen_length: float = 6.0
    required_throughput: float = 0

@router.post("/screening/calculate")
async def calculate_screening(req: ScreenCalcRequest):
    from sandgravel_engine.screening import ScreenCalculator, ScreenParams
    
    params = ScreenParams(
        aperture=req.aperture, wet=req.wet,
        basic_capacity=req.basic_capacity,
        efficiency_factor=req.efficiency_factor,
        deck_factor=req.deck_factor,
        oversize_factor=req.oversize_factor,
        undersize_factor=req.undersize_factor,
        aperture_factor=req.aperture_factor,
        condition_factor=req.condition_factor,
        shape_factor=req.shape_factor,
        moisture_factor=req.moisture_factor,
        safety_factor=req.safety_factor,
        wet_factor=req.wet_factor,
    )
    
    calc = ScreenCalculator()
    result = calc.calculate(params, req.screen_width, req.screen_length, req.required_throughput)
    
    return {
        "unit_capacity": result.unit_capacity,
        "area": result.area,
        "capacity_per_unit": result.capacity_per_unit,
        "num_units": result.num_units,
        "load_factor": result.load_factor,
    }
```

```python
# backend/api/io.py
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
    for name, s in data["streams"].items():
        streams[name] = MaterialStream(
            name=name, tonnage=s["tonnage"],
            grading=SizeDistribution.from_list(s["grading"])
        )
    
    equipment = [EquipmentSelection(**e) for e in data.get("equipment", [])]
    result = BalanceResult(streams=streams, equipment=equipment,
                          iterations=data.get("iterations", 0),
                          convergence_error=data.get("convergence_error", 0))
    
    path = tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False).name
    export_to_excel(result, path)
    return FileResponse(path, filename="balance_result.xlsx")
```

---

## Phase 8: React 前端

### Task 8.1: Vite + React 脚手架

- [ ] **Step 1: 创建Vite项目**

```bash
cd "C:/Users/Admin/Desktop/砂石系统"
npm create vite@latest frontend -- --template react-ts 2>&1 || echo "frontend dir exists"
cd frontend && npm install 2>&1
```

- [ ] **Step 2: 安装依赖**

```bash
cd "C:/Users/Admin/Desktop/砂石系统/frontend"
npm install react-router-dom axios
```

### Task 8.2: 核心组件实现

**Files:**
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/pages/CalculatePage.tsx`
- Create: `frontend/src/components/ParameterPanel.tsx`
- Create: `frontend/src/components/BalanceTable.tsx`
- Create: `frontend/src/components/EquipmentList.tsx`
- Create: `frontend/src/api/client.ts`

- [ ] **Step 1: API客户端**

```typescript
// frontend/src/api/client.ts
import axios from 'axios';

const api = axios.create({ baseURL: 'http://localhost:8000/api' });

export interface BalanceRequest {
  config_name?: string;
  feed_grading?: number[];
  system_throughput?: number;
}

export interface BalanceResponse {
  streams: Record<string, { tonnage: number; grading: number[] }>;
  equipment: Array<{ model: string; quantity: number; unit_capacity: number; load_factor: number }>;
  iterations: number;
  convergence_error: number;
}

export async function calculateBalance(req: BalanceRequest): Promise<BalanceResponse> {
  const { data } = await api.post('/balance/calculate', req);
  return data;
}

export async function getOptions() {
  const { data } = await api.get('/options');
  return data;
}
```

- [ ] **Step 2: App.tsx 路由**

```typescript
// frontend/src/App.tsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import CalculatePage from './pages/CalculatePage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<CalculatePage />} />
      </Routes>
    </BrowserRouter>
  );
}
```

- [ ] **Step 3: CalculatePage 主页面**

```typescript
// frontend/src/pages/CalculatePage.tsx
import { useState } from 'react';
import ParameterPanel from '../components/ParameterPanel';
import BalanceTable from '../components/BalanceTable';
import EquipmentList from '../components/EquipmentList';
import { calculateBalance, BalanceResponse, BalanceRequest } from '../api/client';

export default function CalculatePage() {
  const [result, setResult] = useState<BalanceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [configName, setConfigName] = useState('option1');

  const handleCalculate = async (params: BalanceRequest) => {
    setLoading(true);
    try {
      const data = await calculateBalance({ ...params, config_name: configName });
      setResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: 24 }}>
      <h1>砂石加工系统工艺计算平台</h1>
      <select value={configName} onChange={e => setConfigName(e.target.value)}>
        <option value="option1">方案1 (1500T/H)</option>
        <option value="option2">方案2 (1100T/H)</option>
      </select>

      <ParameterPanel onCalculate={handleCalculate} loading={loading} />

      {result && (
        <>
          <BalanceTable streams={result.streams} iterations={result.iterations} />
          <EquipmentList equipment={result.equipment} />
        </>
      )}
    </div>
  );
}
```

- [ ] **Step 4: ParameterPanel**

```typescript
// frontend/src/components/ParameterPanel.tsx
import { useState } from 'react';
import { BalanceRequest } from '../api/client';

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

interface Props {
  onCalculate: (params: BalanceRequest) => void;
  loading: boolean;
}

export default function ParameterPanel({ onCalculate, loading }: Props) {
  const [grading, setGrading] = useState<number[]>([69, 12, 7, 7, 3, 2]);
  const [throughput, setThroughput] = useState(1500);

  const total = grading.reduce((a, b) => a + b, 0);

  return (
    <div style={{ border: '1px solid #ddd', padding: 16, margin: '16px 0', borderRadius: 8 }}>
      <h3>原料参数</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: 8 }}>
        {grading.map((v, i) => (
          <div key={i}>
            <label>{SIZE_LABELS[i]} mm</label>
            <input type="number" value={v}
              onChange={e => {
                const next = [...grading];
                next[i] = Number(e.target.value);
                setGrading(next);
              }}
              style={{ width: '100%' }} />
          </div>
        ))}
      </div>
      <p style={{ color: Math.abs(total - 100) > 0.1 ? 'red' : 'green' }}>
        合计: {total.toFixed(1)}%
      </p>

      <label>系统处理量 (T/H)</label>
      <input type="number" value={throughput}
        onChange={e => setThroughput(Number(e.target.value))} />

      <button disabled={loading || Math.abs(total - 100) > 0.1}
        onClick={() => onCalculate({ feed_grading: grading, system_throughput: throughput })}>
        {loading ? '计算中...' : '开始计算'}
      </button>
    </div>
  );
}
```

- [ ] **Step 5: BalanceTable**

```typescript
// frontend/src/components/BalanceTable.tsx
interface Props {
  streams: Record<string, { tonnage: number; grading: number[] }>;
  iterations: number;
}

const SIZE_LABELS = ['>150', '150-80', '80-40', '40-20', '20-5', '<5'];

export default function BalanceTable({ streams, iterations }: Props) {
  return (
    <div style={{ marginTop: 24 }}>
      <h3>物料平衡表 (迭代{iterations}次)</h3>
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            <th>名称</th>
            <th>吨位 (t/h)</th>
            {SIZE_LABELS.map(l => <th key={l}>{l}</th>)}
          </tr>
        </thead>
        <tbody>
          {Object.entries(streams).map(([name, stream]) => (
            <tr key={name}>
              <td>{name}</td>
              <td>{stream.tonnage.toFixed(1)}</td>
              {stream.grading.map((v, i) => (
                <td key={i}>{v.toFixed(2)}%</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

- [ ] **Step 6: EquipmentList**

```typescript
// frontend/src/components/EquipmentList.tsx
interface Props {
  equipment: Array<{
    model: string;
    quantity: number;
    unit_capacity: number;
    load_factor: number;
  }>;
}

export default function EquipmentList({ equipment }: Props) {
  return (
    <div style={{ marginTop: 24 }}>
      <h3>设备选型</h3>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 12 }}>
        {equipment.map((eq, i) => (
          <div key={i} style={{
            border: '1px solid #ddd', padding: 12, borderRadius: 8,
            borderLeft: eq.load_factor > 1 ? '4px solid red' : '4px solid green'
          }}>
            <h4>{eq.model}</h4>
            <p>台数: {eq.quantity}</p>
            <p>单机: {eq.unit_capacity} t/h</p>
            <p style={{ color: eq.load_factor > 1 ? 'red' : 'green' }}>
              负荷率: {(eq.load_factor * 100).toFixed(1)}%
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
```

---

## Phase 9: 集成验证 + 黄金数据测试

### Task 9.1: 全流程集成测试

**Files:**
- Create: `tests/fixtures/option1_expected.json`
- Create: `tests/fixtures/option2_expected.json`
- Create: `tests/test_integration.py`

- [ ] **Step 1: 提取Excel黄金数据为JSON**

```python
# 运行此脚本提取Excel数据
import pandas as pd
import json

xls_path = "骨料平衡计算.xls"
xls = pd.ExcelFile(xls_path)

# Sheet2 - 方案1关键行
df2 = pd.read_excel(xls, "中细碎车间平衡计算", header=None)
option1_expected = {
    "jaw_product": [14, 33, 25, 12, 10, 6],
    "combined_after_jaw": [9.66, 34.77, 24.25, 15.28, 9.9, 6.14],
    "final_products": [23.49, 17.61, 17.61, 41.28],
    "system_throughput": 1500,
    "circulating_load_gt40": 1.204819,
    "circulating_load_20_5": 2.791357,
}

with open("tests/fixtures/option1_expected.json", "w") as f:
    json.dump(option1_expected, f, indent=2)
```

- [ ] **Step 2: 编写集成测试**

```python
# tests/test_integration.py
import json
import pytest
from pathlib import Path

FIXTURES = Path(__file__).parent / "fixtures"

@pytest.fixture
def expected_option1():
    with open(FIXTURES / "option1_expected.json") as f:
        return json.load(f)

def test_full_flow_option1(expected_option1):
    """全流程集成测试：方案1"""
    from sandgravel_engine.io import load_yaml_config
    from sandgravel_engine.models import MaterialStream, SizeDistribution
    from sandgravel_engine.crushing import JawCrusher, ConeCrusher, VSICrusher
    from sandgravel_engine.balance import BalanceEngine, FlowConfig, ProcessNode
    
    config = load_yaml_config("option1")
    fg = config["feed_grading"]
    feed = MaterialStream.from_percent("feed", config["system_throughput"],
        [fg.get(k, 0) for k in ["gt150", "_150_80", "_80_40", "_40_20", "_20_5", "lt5"]])
    
    engine = BalanceEngine()
    result = engine.solve(feed, _build_option1_flow())
    
    assert result.iterations > 0
    assert result.convergence_error < 0.001
    
    # 验证产品级配（最终成品4个粒级）
    product_streams = {k: v for k, v in result.streams.items() if "product" in k}
    assert len(product_streams) > 0

def test_full_flow_option2():
    """全流程集成测试：方案2"""
    from sandgravel_engine.io import load_yaml_config
    from sandgravel_engine.models import MaterialStream
    
    config = load_yaml_config("option2")
    fg = config["feed_grading"]
    feed = MaterialStream.from_percent("feed", config["system_throughput"],
        [fg.get(k, 0) for k in ["gt150", "_150_80", "_80_40", "_40_20", "_20_5", "lt5"]])
    
    engine = BalanceEngine()
    result = engine.solve(feed, _build_option1_flow())
    
    assert result.convergence_error < 0.001
```

---

## 验证清单

- [ ] `python -m pytest tests/ -v` — 全部测试通过
- [ ] `cd backend && uvicorn app:app --port 8000` — API启动成功
- [ ] `curl http://localhost:8000/api/options` — 返回JSON
- [ ] `cd frontend && npm run dev` — 前端启动成功
- [ ] 浏览器打开 localhost:5173 — 参数面板 + 计算 + 结果展示正常
- [ ] Excel导出文件可用Excel打开，数值正确
