# Findings: 砂石加工系统

## 源文件解析

| 文件 | 状态 | 核心数据 |
|------|------|----------|
| 3份PDF流程图 | ✅ | 粗碎→预筛分→中碎→第一筛分→制砂→第二筛分 流程骨架 |
| 骨料平衡计算.xls | ✅ | 4 Sheet全部提取：级配平衡、两方案平衡、8组筛分计算 |
| 科研大纲.doc | ⚠️ | GBK解码乱码，仅提取时间线 2015-2017 |

## 关键技术实现

### 1. 破碎工艺参数
- 颚破 Ci125 e=150: 产品级配 [14, 33, 25, 12, 10, 6]%
- 圆锥破 Ci225 e=40: 产品级配 [0, 0, 17, 28, 38, 17]%
- 立轴破 PL9500: 产品比例 40-20:20-5:<5 = 20:50:30

### 2. 筛分11因子公式 Q = B×E×D×V×H×T×K×P×W×S×M
- 4组Excel数据验证通过（80mm干/40mm湿/5mm湿/5mm干）
- 发现: Excel台数为人工录入值，非公式计算 → 采用 ceil 公式

### 3. 两方案差异
| 参数 | Option1 | Option2 |
|------|---------|---------|
| 处理量 | 1500 T/H | 1100 T/H |
| 原料>150mm | 69% | 0% |
| 原料<5mm | 2% | 44% |

### 4. 设备数据库
- Ci125 (颚破 500t/h), Ci225 (圆锥破 420t/h), PL9500 (VSI 180t/h), PL8500 (细砂回收 95t/h)
- 2YKR3060, 3YKR2472, 2YKR2472 振动筛系列

## 踩坑记录

1. **Windows Bash exit code 49**: `python3` 不存在，需用 `python`
2. **Excel num_units 非公式值**: Sheet4 台数为手动录入，ceil公式输出数学最小值
3. **ProcessNode 导入路径**: 在 balance.py 而非 models.py
4. **RecirculationSolver 级配丢失**: 修复为按吨位加权混合新鲜料+循环料
5. **BalanceEngine 未调度节点处理器**: 添加 register_processor() 机制
6. **StaticFiles 拦截动态路由**: heartbeat/shutdown 注册在 StaticFiles(html=True) 之后 → 405 Method Not Allowed。修复：路由移到 mount 之前
7. **PyInstaller sys._MEIPASS 路径**: 打包后 `__file__` 指向 temp 目录 → 所有路径需在 frozen 模式下用 `Path(sys._MEIPASS)`
8. **SVG tooltip 被遮挡**: SVG 按文档序绘制，后续节点覆盖前节点 tooltip → tooltip 统一渲染在最后独立 layer
9. **SVG tooltip 超出 viewBox**: 右侧成品节点 tooltip 延伸至 x=946 (viewBox=830) → tooltip 超出右边界时自动翻到左侧
10. **PDF tooltip 文本溢出**: 148px 框放 3 个粒级值（~40字符/行）需~200px → 3行×2值+190px 宽度
11. **PDF 中文字体编码**: ReportLab 4.x TTFont 内部处理 CID 编码，不生成 Identity-H CMap → 直接搜索 UTF-8 文本无效，需用 pymupdf 提取验证
12. **process_flow.py 硬编码两方案**: Option1/Option2 产品分布和流程结构硬编码为常量 → 重构为 flow_structure dict 透传 API

## 2026-05-13 Session: 前端优化 + PDF 导出 + 流程动态化

### 前端 Industrial Control Room 主题
- 暗色背景 (#080c12) + 噪声纹理 + 径向渐变环境光
- DM Sans / DM Mono 字体，CSS 变量体系
- SVG 滤镜增强：feDropShadow (辉光), feGaussianBlur (边辉光), feComposite (叠加)
- Stagger 进场动画（fadeIn + slideUp，逐元素延迟 0.05s）
- Amber 色 CTA 按钮，绿/红 状态指示（设备负荷率）

### PDF 报告
- reportlab SimpleDocTemplate，A4 暗色主题
- SimHei 中文字体注册（`C:/Windows/Fonts/simhei.ttf`），fallback Helvetica
- 饼图/流程图暂缺，纯表格版报告
- `GET /api/balance/config-defaults?name=option1` 新增端点驱动前端联动

### 流程动态化
- Option1: 11 节点 + 13 边（颚破→预筛分→圆锥破→第一筛分→VS→第二筛分）
- Option2: 7 节点 + 7 边（预筛分→VSI→第二筛分，无粗碎）
- FlowStructure 通过 API 透传，FlowDiagram 纯 props 驱动
- viewBox 根据节点 extents 动态计算
