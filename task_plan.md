# Task Plan: 砂石加工系统工艺计算与设计平台

## 项目目标
基于四份源文件（科研大纲.doc、初拟工艺流程简图.pdf、流程计算简图1/2.pdf、骨料平衡计算.xls），构建：
- A. Python 工艺计算引擎
- B. Web 交互式应用
- C. 工艺设计说明书

---

## Phase 1: 数据提取与模型定义

- [ ] 1.1 完善 .xls 数据提取 — 正确解码所有Sheet中文内容，输出结构化JSON
  - verify: 所有数值与Excel原始值一致
- [ ] 1.2 提取 .doc 科研大纲关键文本（项目背景、技术路线、时间节点）
  - verify: 能提取出中文段落，非乱码
- [ ] 1.3 定义核心数据模型（dataclasses: MaterialStream, SizeDistribution, Equipment, ProcessNode）
  - verify: 能序列化为JSON，类型检查通过
- [ ] 1.4 将 Excel 中的两套工况参数抽取为 YAML 配置文件
  - verify: 反序列化后参数值与Excel一致

## Phase 2: Python 计算引擎核心

- [ ] 2.1 物料平衡引擎 (balance.py) — 实现迭代收敛算法，支持开路/闭路循环
  - verify: 平衡结果与 Excel Sheet2/Sheet3 误差 < 0.01%
- [ ] 2.2 破碎模型 (crushing.py) — 颚破/圆锥破/立轴破的排矿口-产品粒度关系
  - verify: 各粒级产率与 Excel 第7-17行一致
- [ ] 2.3 筛分模型 (screening.py) — BEDVHTKPWSM 11因子公式，干法/湿法筛分
  - verify: 筛分面积/台数与 Excel Sheet4 一致
- [ ] 2.4 设备选型模块 (equipment.py) — 根据计算负荷匹配设备库，输出台数+负荷率
  - verify: 选型结果与 Excel 第54-62行一致
- [ ] 2.5 流程编排引擎 (process_flow.py) — 定义流程节点图，驱动全流程计算
  - verify: 运行 Option1/Option2 全流程，输出一致性验证

## Phase 3: 测试与验证

- [ ] 3.1 单元测试 — 每个核心模块覆盖率 > 90%
- [ ] 3.2 集成测试 — Option1/Option2 全流程回归测试
- [ ] 3.3 黄金数据对比 — 将 Excel 关键行作为 pytest fixture 逐行对比

## Phase 4: Web 应用

- [ ] 4.1 FastAPI 后端 — 封装计算引擎为 REST API
- [ ] 4.2 React 前端 — 参数输入表单 + 交互式流程图 + 结果表格
- [ ] 4.3 计算报告导出（Excel/PDF）

## Phase 5: 设计说明书

- [ ] 5.1 整合四份源文件内容为 .md 设计文档
- [ ] 5.2 嵌入计算验证结果与设备清单
- [ ] 5.3 中英文双语关键术语

---

## 关键决策记录
| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| 1 | 使用 FastAPI + React | 轻量、适合科学计算展示 | 2026-05-12 |
| 2 | 配置文件用 YAML | 可读性优于 JSON，便于工艺参数调整 | 2026-05-12 |
