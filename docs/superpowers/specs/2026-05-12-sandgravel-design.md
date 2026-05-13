# 砂石加工系统工艺计算平台 — 设计文档

## 1. 项目背景

基于四份源文件构建砂石骨料加工系统的工艺计算与设计平台：
- 砂石系统工艺科技项目科研大纲.doc
- 附图1 初拟工艺流程简图-Model.pdf
- 附图2 流程计算简图1-Model.pdf
- 附图3 流程计算简图2-Model.pdf
- 骨料平衡计算.xls（4个Sheet）

## 2. 需求澄清

| 维度 | 决策 |
|------|------|
| 使用场景 | 工程设计院（新项目设计+方案对比）+ 现场生产运维（参数快速调整） |
| 部署方式 | 单机桌面应用，本地浏览器访问 |
| 输入方式 | YAML配置文件 + Web界面手动输入 + Excel导入，三种方式可切换 |
| 流程灵活性 | 先固定两套方案(1500T/H + 1100T/H)，架构预留扩展接口 |
| 交付物 | Python计算引擎 + Web交互应用 + 设计说明书 |

## 3. 方案选择

**选择方案B：FastAPI + React 分离式架构**

理由：
- 计算核心可脱离Web独立CLI运行（契合生产运维场景）
- React实现交互式工艺流程图，点击节点查看详情
- 架构预留扩展接口，支持后续自定义流程编排
- 两套方案共用同一计算引擎

## 4. 架构设计

### 4.1 三层分离

```
第1层：sandgravel_engine/    纯Python计算核心，零Web依赖
第2层：backend/              FastAPI薄层，序列化+验证+路由
第3层：frontend/             React SPA，交互式可视化
```

数据流：YAML/Excel → Engine计算 → JSON → API序列化 → HTTP → React渲染

### 4.2 启动方式

```bash
# CLI模式（运维场景）
python -m sandgravel_engine --config option1.yaml --output result.xlsx

# Web模式（设计场景）
cd backend && uvicorn app:app --port 8000
cd frontend && npm run dev
```

## 5. 计算引擎模块

### 5.1 balance.py — 物料平衡引擎
- 核心算法：迭代收敛至 |δ| < 0.0001
- 开路循环：一次通过
- 闭路循环：>40mm碎石约5次收敛，20-5mm制砂约17次收敛
- 输入：FlowConfig（流程DAG + 原料参数）
- 输出：BalanceResult（全部节点物料流 + 收敛信息）

### 5.2 crushing.py — 破碎产率模型
- JawCrusher(e=150)：开路粗碎，产品级配基于Excel第6-7行
- ConeCrusher(e=40)：闭路中碎
- VSICrusher(PL9500)：闭路制砂，产品级配比例 20:50:30

### 5.3 screening.py — 筛分11因子公式
- Q = B × E × D × V × H × T × K × P × W × S × M (t/m²·h)
- 支持干法/湿法两种模式（湿法 M=1.9）
- 输出：所需筛分面积 → 台数 → 负荷率

### 5.4 equipment.py — 设备选型
- 设备库：Ci125(颚破500t/h), Ci225(圆锥破420t/h), PL9500(立轴破), PL8500(细砂回收), 2YKR/3YKR系列筛
- 逻辑：计算负荷 / 单机能力 → 台数(向上取整) → 负荷率 = 实际/额定

### 5.5 process_flow.py — 流程编排
- ProcessNode类型：Crusher, Screen, Splitter, Sink
- 流程DAG拓扑排序驱动计算
- 预定义：option1 (1500T/H, 原料细料19.2%), option2 (1100T/H, 原料细料25.2%)

### 5.6 数据模型

```python
@dataclass
class SizeDistribution:
    gt150: float = 0; _150_80: float = 0; _80_40: float = 0
    _40_20: float = 0; _20_5: float = 0; lt5: float = 0

@dataclass
class MaterialStream:
    name: str
    tonnage: float
    grading: SizeDistribution
    moisture: float = 0

@dataclass
class EquipmentSelection:
    model: str
    quantity: int
    unit_capacity: float
    load_factor: float

@dataclass  
class BalanceResult:
    streams: dict[str, MaterialStream]
    equipment: list[EquipmentSelection]
    iterations: int
    convergence_error: float
```

## 6. API 设计

| 方法 | 路径 | 功能 |
|------|------|------|
| POST | /api/balance/calculate | 执行平衡计算 |
| POST | /api/equipment/select | 设备选型 |
| POST | /api/screening/calculate | 筛分计算 |
| POST | /api/io/import-excel | Excel导入 |
| POST | /api/io/export-excel | Excel导出 |
| GET | /api/options | 获取可用方案+设备库 |

## 7. 前端设计

### 7.1 页面路由
- `/` — 主计算页（参数面板 + 流程图 + 结果表）
- `/compare` — 方案对比（Option1 vs Option2）
- `/equipment` — 设备库浏览

### 7.2 核心组件
- **FlowDiagram** — 交互式SVG流程图，节点可点击，流线标注实时数据
- **ParameterPanel** — 可折叠参数面板（原料级配、破碎机、筛分机、处理量）
- **BalanceTable** — 物料平衡表，可展开迭代收敛详情
- **EquipmentList** — 设备选型结果卡片

## 8. 测试策略

**黄金数据验证法**：将Excel原始计算结果作为预期值，pytest逐个对比。

| 测试模块 | 验证内容 | 黄金数据源 | 容差 |
|----------|----------|-----------|------|
| test_balance | 各粒级产率% | Sheet2 第8-52行 | ±0.01% |
| test_crushing | 破碎产品级配 | Sheet2 第6-8行 | ±0.01% |
| test_screening | 筛分面积/台数 | Sheet4 全8组 | ±0.1% |
| test_integration | 全流程Option1+2 | Sheet2+3汇总 | ±0.01% |

## 9. 错误处理

- 级配之和≠100% → 拒绝计算，提示修正
- 迭代超100次未收敛 → ConvergenceError + 当前残差
- 设备负荷率>100% → 警告（红色标记），不阻断
- Excel导入 → 按表头匹配列，不依赖固定位置
- API层 → Pydantic校验，非法参数返回422

## 10. 项目结构

```
砂石系统/
├── sandgravel_engine/    # Python计算核心
│   ├── balance.py, crushing.py, screening.py
│   ├── equipment.py, process_flow.py, io.py, models.py
│   └── config/option1.yaml, option2.yaml
├── backend/              # FastAPI
│   ├── app.py
│   └── api/balance.py, equipment.py, screening.py, io.py
├── frontend/             # React (Vite)
│   └── src/ (App, pages/, components/, api/, types/)
├── tests/                # pytest + 黄金数据fixtures
├── docs/superpowers/specs/
├── task_plan.md, findings.md, progress.md
```
