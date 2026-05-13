# Claude Code 完整开发 Workflow 操作指南

> 从"一句话需求"到"高质量交付"的完整流水线，每一步都有具体命令和文件。

---

## 〇、30秒速览

```
你：帮我做一个用户认证系统

Claude：（自动触发 brainstorming）先别写代码，我确认几个问题...
       → 设计文档 → 你审批
       → 任务拆解 → task_plan.md
       → TDD 逐步实现 → 每步打勾
       → Code Review → 多维度审查
       → 交付（测试全绿 + progress.md 完整记录）

全程你不用记步骤 —— Skills 在每个关卡自动触发。
```

---

## 一、前置准备：安装三个必装 Skill

### 1.1 Superpowers（设计关卡 + 执行关卡 + 质量关卡）

```bash
# 方法 A：官方插件市场（推荐）
/plugin install superpowers@claude-plugins-official

# 方法 B：Superpowers 市场（含更多配套插件）
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace
```

**包含的核心子能力（全部自动触发，无需手动调用）：**

| 子能力 | 触发时机 | 做什么 |
|--------|----------|--------|
| `brainstorming` | 任何编码之前 | 苏格拉底式追问，输出设计文档 |
| `writing-plans` | 设计审批通过后 | 将设计拆成 2-5 分钟一个的 bite-sized 任务 |
| `test-driven-development` | 执行编码时 | 严格执行 RED-GREEN-REFACTOR |
| `subagent-driven-development` | 执行计划时 | 每个任务派一个全新子 Agent，两阶段 review |
| `requesting-code-review` | 任务间 | 对照计划审查，严重问题阻断进度 |
| `using-git-worktrees` | 设计审批后 | 创建隔离的 git worktree 分支 |
| `finishing-a-development-branch` | 所有任务完成 | 验证测试 → 展示合并选项 → 清理 worktree |

### 1.2 Planning with Files（进度关卡）

```bash
# 方法 A：npx 安装（推荐，会自动放置到正确路径）
npx skills add OthmanAdi/planning-with-files --skill planning-with-files-zh -g

# 方法 B：Claude Code 插件（含 /plan 自动补全）
/plugin marketplace add OthmanAdi/planning-with-files
/plugin install planning-with-files@planning-with-files
```

### 1.3 可选增强

```bash
# 防止半途而废
npx skills add OthmanAdi/ralph-loop -g

# 代码精简
npx skills add OthmanAdi/code-simplifier -g
```

---

## 二、Workflow 全景图：5 个关卡 × 4 个阶段

```
┌──────────────────────────────────────────────────────────────────┐
│                                                                  │
│  阶段 1              阶段 2             阶段 3         阶段 4     │
│  想清楚              拆任务             写代码         保质量     │
│                                                                  │
│  ┌─────────┐       ┌─────────┐       ┌─────────┐    ┌─────────┐ │
│  │关卡 1   │  →    │关卡 2   │  →    │关卡 3   │ → │关卡 4   │ │
│  │设计审批 │       │计划文件 │       │TDD执行  │    │Code     │ │
│  │         │       │落盘     │       │每步打勾 │    │Review   │ │
│  └─────────┘       └─────────┘       └─────────┘    └─────────┘ │
│                                                                  │
│  负责 Skill:        负责 Skill:       负责 Skill:    负责 Skill: │
│  Superpowers        Planning with     Superpowers    Superpowers │
│  brainstorming      Files             TDD + SubAgent code-review │
│                                                                  │
│  产出:               产出:             产出:          产出:       │
│  设计文档            task_plan.md      代码+测试      review报告  │
│  (方案对比+推荐)     findings.md       progress.md               │
│                     progress.md                                  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 三、阶段 1：想清楚 —— 用 brainstorming 把模糊需求变成设计文档

### 3.1 触发条件

**满足任一条件就要走 brainstorming：**
- 任务描述超过 3 句话
- 涉及 3 个及以上文件改动
- 有架构选择（选什么库、什么模式、什么数据库）
- 你心里对"具体怎么做"没有 100% 把握

> 别跳过。简单任务的设计可以只有 3-5 行，但必须显式呈现并获得你的确认。

### 3.2 具体操作

**步骤 1：你发起任务**

```
你：帮我做一个用户登录功能，支持 JWT 和 refresh token
```

**步骤 2：brainstorming 自动激活**

Superpowers 的 brainstorming 技能会在你写任何代码之前自动拦截，执行 9 步流程：

| 步骤 | Claude 的行为 | 你要做什么 |
|------|--------------|-----------|
| 1 | 探索项目上下文（文件、文档、最近 commit） | 等 |
| 2 | 如涉及视觉问题，提供视觉辅助选项 | 选 yes/no |
| 3 | 逐一提问澄清需求（一次只问一个问题） | 逐一回答 |
| 4 | 提出 2-3 种方案，附权衡和推荐 | 选择方案 |
| 5 | 分段展示设计（架构 → 组件 → 数据流 → 错误处理 → 测试） | 逐段审批 |
| 6 | 设计审批通过，写入设计文档 | 等 |
| 7 | 自检设计文档（占位符、矛盾、歧义、范围） | 等 |
| 8 | 请你审核书面 spec 文件 | **仔细读 spec 文件，确认或提修改** |
| 9 | 审批通过，自动调用 writing-plans | 等 |

**步骤 3：产出设计文档**

文件位置：`docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`

内容包含：
- 需求澄清（目的、约束、成功标准）
- 2-3 种可选方案 + 推荐方案及理由
- 架构、组件、数据流、错误处理、测试策略

### 3.3 关键命令

```bash
# 如果 brainstorming 没有自动触发，手动激活：
/superpowers:brainstorm

# 查看已有的设计文档
ls docs/superpowers/specs/
```

### 3.4 关卡验证清单

- [ ] 设计文档已写并获你批准
- [ ] 至少对比了 2 种方案
- [ ] 明确了成功标准
- [ ] 你完整读过 spec 文件并同意

---

## 四、阶段 2：拆任务 —— 用 Planning with Files 把设计变成可追踪的计划

### 4.1 触发条件

设计文档审批通过后，Superpowers 的 `writing-plans` 会自动将设计拆成 bite-sized 任务。然后你立即启动 Planning with Files。

### 4.2 具体操作

**步骤 1：启动 Planning with Files**

```
/planning-with-files:plan
```

或者直接用简写：

```
/plan
```

**步骤 2：Claude 创建三个文件**

Claude 会基于 Superpowers 产出的设计文档，在当前工作目录创建：

```
当前任务目录/
├── task_plan.md   ← 任务拆解、阶段规划、checklist
├── findings.md    ← 调研结论、踩过的坑、中间发现
└── progress.md    ← 会话日志、每步完成状态
```

**步骤 3：审视 task_plan.md**

典型结构：

```markdown
# 任务：用户认证模块

## 阶段 1：数据库与模型
- [ ] 创建 User 模型（users 表迁移）
- [ ] 创建 RefreshToken 模型
- [ ] 编写迁移回滚脚本

## 阶段 2：业务逻辑
- [ ] JWT 生成与验证服务
- [ ] Refresh Token 轮换逻辑
- [ ] 密码哈希工具

## 阶段 3：API 接口
- [ ] POST /auth/register
- [ ] POST /auth/login
- [ ] POST /auth/refresh
- [ ] 中间件：JWT 鉴权

## 阶段 4：测试
- [ ] 单元测试：auth service
- [ ] 集成测试：API 接口
- [ ] E2E 测试：登录全流程

## 阶段 5：文档与收尾
- [ ] API 文档更新
- [ ] 环境变量说明
```

**步骤 4：查看进度（随时可用）**

```
/planning-with-files:status
```

输出示例：
```
📋 任务进度总览
━━━━━━━━━━━━━━━━━━━━━━
✅ 阶段 1：数据库与模型 (3/3)
🔄 阶段 2：业务逻辑 (1/3) ← 当前
⏳ 阶段 3：API 接口 (0/4)
⏳ 阶段 4：测试 (0/3)
⏳ 阶段 5：文档与收尾 (0/2)
━━━━━━━━━━━━━━━━━━━━━━
总进度: 4/15 (26.7%)
```

### 4.3 关键命令

```bash
/plan                    # 开始规划（简写）
/planning-with-files:plan     # 完整命令
/planning-with-files:status   # 查看进度
/planning-with-files:start    # 原始启动命令
```

### 4.4 关卡验证清单

- [ ] task_plan.md 已创建，内容覆盖全部阶段
- [ ] 每个子任务小于 5 分钟可独立完成
- [ ] 依赖关系清晰
- [ ] findings.md 和 progress.md 已初始化

---

## 五、阶段 3：写代码 —— TDD + SubAgent 驱动执行

### 5.1 触发条件

task_plan.md 就绪后，开始逐个任务执行。Superpowers 的 TDD 和 SubAgent 技能自动激活。

### 5.2 具体操作

**执行过程是自动化的：**

```
对 task_plan.md 中的每个子任务：

  1. SubAgent 被派发（全新上下文，专注单一任务）
     │
  2. RED：先写失败的测试
     │
  3. 确认测试确实失败（不是假阳性）
     │
  4. GREEN：写最小代码让测试通过
     │
  5. REFACTOR：消除重复，保持简洁
     │
  6. 两阶段 SubAgent Review：
     ├── Stage 1：对照 spec 检查功能完整性
     └── Stage 2：检查代码质量（安全、性能、可维护性）
     │
  7. Review 通过 → task_plan.md 打勾 → 下一个任务
     不通过 → 自动修复 → 重新 review
```

**你只需要：**
- 在每个任务间确认方向正确
- 每 2-3 个任务检视一次 `progress.md`
- 遇到需要决策的地方 Claude 会主动问你

**重要：每 2 次工具调用后 Claude 会自动把发现写入 `findings.md`**

### 5.3 跨会话恢复（关键能力）

上下文满了怎么办？

```
/clear
```

然后直接说：

```
继续
```

Planning with Files 会自动：
1. 检测上次会话的进度文件
2. 找到 task_plan.md 最后更新的时间
3. 提取后续丢失的上下文
4. 展示 catchup 报告，无缝接续

> 建议在 `settings.json` 中设置 `"autoCompact": false`，让你能主动控制在最有价值的时机 `/clear`，最大化恢复信息量。

### 5.4 调试与错误处理

遇到 bug 时，Superpowers 的 `systematic-debugging` 自动介入：

| 阶段 | 做什么 |
|------|--------|
| 1. 复现 | 创建最小复现用例 |
| 2. 诊断 | 系统性追踪根因（不是猜） |
| 3. 修复 | 最小化修改 |
| 4. 验证 | `verification-before-completion` 确认真的修好了 |

错误信息会自动写入 `findings.md`，同一个坑不踩两次。

### 5.5 关键命令

```bash
# 查看当前进度
/planning-with-files:status

# 上下文清空后恢复
/clear
继续

# 如果需要手动激活子 Agent 模式
/superpowers:execute-plan
```

### 5.6 关卡验证清单

- [ ] 每个子任务：测试先于实现代码
- [ ] 每个子任务完成：测试通过 + 无 lint 错误
- [ ] findings.md 记录了踩坑经验
- [ ] progress.md 有每一步的完成记录

---

## 六、阶段 4：保质量 —— Code Review + 分支合并

### 6.1 触发条件

所有 task_plan.md 子任务打勾完成后。

### 6.2 具体操作

**步骤 1：Code Review（自动触发）**

```
# 如果没自动触发，手动调用：
/superpowers:code-review
```

Superpowers 的 `requesting-code-review` 做多维度审查：

| 维度 | 内容 | 严重程度 |
|------|------|----------|
| 功能完整性 | 对照 spec/task_plan.md，有无遗漏？ | Critical 阻断 |
| 安全性 | SQL 注入、XSS、未校验输入、密钥泄露 | Critical 阻断 |
| 代码规范 | 命名、结构、DRY 原则 | Warning |
| 性能 | N+1 查询、不必要循环、内存泄漏 | Warning |
| 测试覆盖 | 边界条件、异常路径 | Warning |

Critical 问题必须修复才能进入下一步。

**步骤 2：分支完成**

Superpowers 的 `finishing-a-development-branch` 自动执行：

```
1. 验证全部测试通过
2. 展示选项：
   ├── 合并到主分支（merge）
   ├── 创建 PR（pull request）
   ├── 保留分支
   └── 丢弃
3. 清理 worktree
```

**步骤 3：收尾记录**

`progress.md` 中记录：
- 本次会话做了什么
- 关键决策及原因
- 已知问题和后续事项

### 6.3 关键命令

```bash
# 手动调用 code review
/superpowers:code-review

# 查看完整进度日志
cat progress.md

# 查看踩坑记录
cat findings.md

# Git 提交（commit message 引用 task_plan.md）
git add -A
git commit -m "feat(auth): 用户认证模块重构

完成 task_plan.md 中 5 个阶段共 15 个子任务。
设计文档: docs/superpowers/specs/2026-05-12-auth-design.md"
```

### 6.4 关卡验证清单

- [ ] Review 通过（无 Critical 问题）
- [ ] 全部测试通过
- [ ] progress.md 记录完整（含关键决策）
- [ ] findings.md 中所有坑都有解决方案
- [ ] task_plan.md 全部打勾

---

## 七、三种场景 Workflow 速查

### 场景 A：Bug 修复（轻量级，5-15 分钟）

```
触发条件：修 bug、单文件小改动、typo fix
```

| 步骤 | 动作 | 命令/工具 |
|------|------|-----------|
| 1 | 创建轻量 checklist | 在 progress.md 写 3 行 |
| 2 | 写复现测试 | Superpowers TDD（自动） |
| 3 | 修代码 | Claude Code 原生 |
| 4 | 跑测试验证 | Claude Code 原生 |
| 5 | 记录修复原因 | 写入 progress.md 一行 |

> 不加载 brainstorming，不创建 task_plan.md。只用一个 progress.md 追踪。

### 场景 B：新功能开发（标准级，30 分钟 - 2 小时）

```
触发条件：新 API、新组件、2-10 个文件改动
```

| 步骤 | 动作 | 命令/工具 | 产出 |
|------|------|-----------|------|
| 1 | 需求澄清 | brainstorming（自动） | 3-5 行设计摘要 |
| 2 | 任务拆解 | `/plan` | task_plan.md |
| 3 | 逐步实现 | TDD（自动），每步打勾 | 代码 + 测试 |
| 4 | 自我审查 | code-review（自动） | review 报告 |
| 5 | Git 提交 | 手动 commit | 引用 task_plan.md |

### 场景 C：系统级重构（重量级，半天 - 数天）

```
触发条件：架构变更、跨模块、10+ 文件、跨多个会话
```

| 步骤 | 动作 | 命令/工具 | 产出 |
|------|------|-----------|------|
| 1 | 完整需求讨论 | brainstorming（自动） | 设计文档（方案对比+推荐） |
| 2 | 开 git worktree | using-git-worktrees（自动） | 隔离工作空间 |
| 3 | 任务拆解 | `/plan` | task_plan.md（含依赖图） |
| 4 | 子 Agent 并行开发 | subagent-driven-development（自动） | 并行推进子任务 |
| 5 | 逐个验证 | TDD 红-绿-重构 | 独立验证 |
| 6 | 跨会话恢复 | `/clear` → `继续` | 自动恢复进度 |
| 7 | 多维度审查 | code-review（自动） | bug/安全/规范三份报告 |
| 8 | 合并 + 记录 | finishing-a-development-branch（自动） | progress.md 作为 commit body |

---

## 八、CLAUDE.md 推荐配置

把以下内容加到项目根目录或 `~/.claude/CLAUDE.md`（全局生效）：

```markdown
## Workflow 自动规则

### 任务复杂度判断
- 简单任务（≤2 文件，无架构影响）：直接做，跳过 brainstorming
- 标准任务（3-10 文件）：完整 brainstorming → /plan → 执行
- 大型任务（10+ 文件或架构变更）：brainstorming → /plan → TDD + SubAgent → review

### 关卡硬性要求
1. 编码前：设计文档获批准（标准级及以上任务）
2. 执行中：task_plan.md 每完成一步打勾 [x]
3. 每 2 次工具调用后：发现写入 findings.md
4. 提交前：测试全绿 + lint 无错误 + review 通过

### 文件约定
- 设计文档：docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md
- 任务计划：当前工作目录下 task_plan.md
- 踩坑记录：findings.md
- 会话日志：progress.md

### 禁令（写死在关卡里）
- 不可以在未获批准的情况下开始大规模重构
- 不可以跳过测试直接交付功能
- 不可以交付"框架搭好了你自己完善"的半成品
- 不可以重复踩同一个坑（去读 findings.md）
```

---

## 九、核心原则（记住这 5 条就够了）

### 1. 关卡思维 > 流程思维

```
Bad： 设计 → 规划 → 编码 → 测试 → 文档 → 审查 → 部署 → 监控
Good：编码 ← [关卡：测试通过了吗？] → 审查 ← [关卡：安全检查通过了吗？] → 交付
```

每个关卡**拦截 AI 最容易犯的一类错误**。关卡的成本必须低于它拦截的错误成本。

### 2. 文件系统 = 长期记忆，上下文 = 短期记忆

| 存什么 | 存哪里 | 为什么 |
|--------|--------|--------|
| 设计决策 | `docs/superpowers/specs/` | 事后能回溯为什么这么设计 |
| 任务进度 | `task_plan.md` | 上下文清空后能恢复 |
| 踩过的坑 | `findings.md` | 同一个坑不踩两次 |
| 会话日志 | `progress.md` | 跨天/跨周的任务能接上 |

### 3. 简单任务不加关卡

一个 typo fix 不需要 brainstorming。公式：

```
关卡的 token 成本 + 时间成本 < 没有关卡时出错的修复成本 × 出错概率
```

### 4. 渐进式安装 Skill

```
第一周：只装 Planning with Files
第二周：需要方向把关 → 加 Superpowers
第三周：发现 Claude 总半途而废 → 加 Ralph Loop
第四周：代码质量需要提升 → 加 Code Simplifier
```

一次装 10 个 Skill = 上下文被吃满 + 你不知道哪个有用。日常常驻 ≤ 3 个。

### 5. Workflow 规则写在 CLAUDE.md 里

CLAUDE.md 是每个会话启动时自动加载的。写在里面的规则会被无条件执行。不要依赖"我会记得告诉 Claude"——写到文件里。

---

## 十、安装清单（一次性操作）

```bash
# 1. Superpowers（设计+执行+质量三关卡）
/plugin install superpowers@claude-plugins-official

# 2. Planning with Files（进度关卡，中文版）
npx skills add OthmanAdi/planning-with-files --skill planning-with-files-zh -g

# 3. Ralph Loop（防甩锅，可选）
npx skills add OthmanAdi/ralph-loop -g

# 4. 在 ~/.claude/settings.json 中关闭自动压缩（可选，增强跨会话恢复）
# 添加: "autoCompact": false

# 5. 将本文档第八节的 CLAUDE.md 配置写入 ~/.claude/CLAUDE.md
```

完成后重启 Claude Code 即可生效。

---

## 十一、Cheat Sheet

| 你想做什么 | 用什么 | 一句话 |
|-----------|--------|--------|
| 动手前想清楚 | brainstorming（自动） | 苏格拉底式追问，产出设计文档 |
| 把任务拆解并追踪 | `/plan` | 创建 task_plan/findings/progress 三文件 |
| 看当前进度 | `/planning-with-files:status` | 展示各阶段完成百分比 |
| 上下文清空后恢复 | `/clear` → `继续` | 自动从文件恢复进度 |
| 强制 TDD | TDD（自动） | 红-绿-重构循环 |
| 并行加速 | subagent-driven-development（自动） | 每个任务派全新子 Agent |
| 代码质量把关 | code-review（自动） | 多维度审查，Critical 阻断 |
| 防止半途而废 | Ralph Loop（自动） | 拦截甩锅行为 |
| Bug 修复 | 手写 3 行 checklist | 不加载任何 Skill，只用 progress.md |
| 新手上路最小配置 | Planning with Files | 只装这一个 |

---

## 十二、一句话总结

> **Superpowers** 在每个关卡自动拦截 AI 最容易犯的错误（方向跑偏、质量崩坏、测试缺失），**Planning with Files** 把一切重要信息落盘确保不会丢失。两者配合 = 方向正确 + 执行到位 + 进度可见 + 跨会话无缝接续。

*参考来源：*
- *[obra/superpowers](https://github.com/obra/superpowers) — Superpowers 官方仓库（~16k stars）*
- *[OthmanAdi/planning-with-files](https://github.com/OthmanAdi/planning-with-files) — Planning with Files 官方仓库*
- *小红书 Claude Code 使用技巧与 Skills 推荐（2026-05）*
- *社区实践总结：Superpowers × Planning with Files 协同使用指南*
- *用 Skills 构建 Workflow 方法论*
