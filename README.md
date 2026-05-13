# 砂石加工系统工艺计算平台

基于 Excel 黄金数据验证的砂石骨料加工系统工艺设计工具。支持工艺流程设计、物料平衡计算、设备选型、Excel 导入导出、交互式流程图可视化。

## 下载

**[SandGravelCalc.exe](https://github.com/lyz-wave/sandgravel-process-calc/releases/latest)** (31MB) — 单文件桌面应用，双击即用，无需安装任何依赖。

### 常见问题

**双击无反应？** 按顺序排查：

1. **Windows Defender 拦截** — 右键 exe → 属性 → 勾选「解除锁定」→ 确定。或双击时点击「更多信息」→「仍要运行」
2. **端口被占用** — 之前的实例未关闭。打开任务管理器，结束所有 `SandGravelCalc.exe` 进程后重试
3. **查看启动日志** — 桌面上的 `SandGravelCalc_startup.log` 记录了启动过程，崩溃时会弹窗显示具体错误
4. **手动诊断** — Win+R → `cmd` → 把 exe 拖进命令行窗口 → 回车，可直接看到错误输出

## 快速开始

```bash
# CLI 模式（生产运维）
python -m sandgravel_engine --config option1
python -m sandgravel_engine --config option2 --throughput 1200 --output result.xlsx

# Web 模式（工程设计）
cd backend && uvicorn app:app --port 8000 &
cd frontend && npm run dev
# 浏览器打开 http://localhost:5173
```

## 功能

| 功能 | CLI | Web |
|------|:---:|:---:|
| 物料平衡计算（迭代收敛） | ✅ | ✅ |
| 破碎产率模型（颚破/圆锥破/立轴破） | ✅ | ✅ |
| 筛分设备选型（BEDVHTKPWSM 11因子） | ✅ | ✅ |
| YAML 配置文件 | ✅ | ✅ |
| Excel 导出/导入 | ✅ | ✅ |
| 交互式 SVG 流程图 | — | ✅ |
| 方案对比（Option1 vs Option2） | — | ✅ |
| 参数面板实时计算 | — | ✅ |

## 架构

```
用户输入 (CLI / YAML / Excel / Web UI)
        │
        ▼
┌─────────────────────────┐
│  sandgravel_engine/     │  ← Python 计算核心（零 Web 依赖）
│  models    balance      │
│  crushing  screening    │
│  equipment process_flow │
│  io        __main__     │
└───────────┬─────────────┘
            │ JSON
┌───────────▼─────────────┐
│  backend/ (FastAPI)     │  ← API 层
│  6 REST endpoints       │
└───────────┬─────────────┘
            │ HTTP
┌───────────▼─────────────┐
│  frontend/ (React+Vite) │  ← UI 层
│  FlowDiagram ComparePage│
└─────────────────────────┘
```

## 两方案对比

| 产品 | 方案1 (1500T/H 爆破毛料) | 方案2 (1100T/H 天然砂石料) |
|------|:---:|:---:|
| 40-80mm 粗骨料 | 23.49% | 0% |
| 40-20mm | 17.61% | 27.75% |
| 20-5mm | 17.61% | 22.70% |
| <5mm 机制砂 | 41.28% | 49.54% |
| 颚破 | 3×Ci125 | 旁路 |
| 圆锥破 | 3×Ci225 | 3×Ci225 |
| 立轴破 | 6×PL9500 | 6×PL9500 |

## 测试

```bash
python -m pytest tests/ -v
# 58 passed in 0.6s
```

覆盖全部计算模块，关键数据与 Excel 原始值误差 < 0.02%。

## 项目结构

```
砂石系统/
├── sandgravel_engine/    # 计算核心
│   ├── models.py         # SizeDistribution, MaterialStream, etc.
│   ├── balance.py        # BalanceEngine + RecirculationSolver
│   ├── crushing.py       # JawCrusher / ConeCrusher / VSICrusher
│   ├── screening.py      # BEDVHTKPWSM 11因子筛分
│   ├── equipment.py      # 设备数据库 + 选型
│   ├── process_flow.py   # 流程编排引擎
│   ├── io.py             # YAML / Excel / JSON 读写
│   ├── __main__.py       # CLI 入口
│   └── config/           # option1.yaml, option2.yaml
├── backend/              # FastAPI
│   ├── app.py
│   └── api/              # balance, equipment, screening, io
├── frontend/             # React + Vite
│   └── src/
│       ├── pages/        # CalculatePage, ComparePage
│       ├── components/   # FlowDiagram, ParameterPanel, etc.
│       └── api/          # client.ts
├── tests/                # 58 tests
└── docs/                 # 设计文档
```

## Excel 导入模板

`insert/导入模板.xlsx` 包含 3 个 Sheet：

| Sheet | 必填 | 内容 |
|-------|:---:|------|
| 物料平衡 | ✅ | 名称 / 吨位(t/h) / >150 / 150-80 / 80-40 / 40-20 / 20-5 / <5 |
| 设备选型 | — | 型号 / 台数 / 单机能力(t/h) / 实际通过量(t/h) / 负荷率 |
| 收敛信息 | — | 迭代次数 / 收敛误差 |

Web 界面点击「导入 Excel」上传，或 CLI：`python -m sandgravel_engine --config your_config.yaml`

## 源文件依据

- 砂石系统工艺科技项目科研大纲.doc（12 项研究内容）
- 附图1 初拟工艺流程简图-Model.pdf
- 附图2 流程计算简图1-Model.pdf
- 附图3 流程计算简图2-Model.pdf
- 骨料平衡计算.xls（级配平衡 + 中细碎平衡 + 筛分选型）

## 依赖

**Python:** `pip install fastapi uvicorn pyyaml openpyxl pandas`

**Node:** `cd frontend && npm install`
