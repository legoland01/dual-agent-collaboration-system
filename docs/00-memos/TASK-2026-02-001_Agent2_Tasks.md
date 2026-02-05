# Agent 2 任务清单

**文档编号**: TASK-2026-02-001
**日期**: 2026-02-03
**发起人**: Agent 1 (产品经理)
**状态**: 待执行

---

## 背景

详见以下已推送的文档（请先执行 `git pull`）：

| 文档 | 位置 | 说明 |
|------|------|------|
| MEMO-2026-02-004 | docs/00-memos/MEMO-2026-02-004_AI_Agent_Engineering_Process.md | 5-Why 分析 + 解决方案 |
| MEMO-2026-02-004-ADDENDUM | docs/00-memos/MEMO-2026-02-004-ADDENDUM_Dynamic_Checklist.md | 动态 checklist 机制设计 |
| TREATISE-2026-02-001 | docs/06-experience/TREATISE-2026-02-001_Human_AI_Collaborative_Software_Engineering.md | 完整论文（可选阅读） |

---

## 任务一：评审并签署 MEMO-2026-02-004

### 行动

```bash
# 1. 拉取最新文档
git pull

# 2. 阅读 MEMO-2026-02-004
cat docs/00-memos/MEMO-2026-02-004_AI_Agent_Engineering_Process.md

# 3. 创建评审意见
cat > docs/00-memos/MEMO-2026-02-004_Review_Agent2.md << 'EOF'
# MEMO-2026-02-004 评审意见 - Agent 2

## 评审意见

[填写你的评审意见]

## 签署确认

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 作者 | Agent 1 | 2026-02-03 | ✅ |
| 评审 | Agent 2 | [日期] | ✅ / ❌ |
EOF

# 4. 提交
git add docs/00-memos/MEMO-2026-02-004_Review_Agent2.md
git commit -m "docs: Agent 2 review - MEMO-2026-02-004"
git push
```

---

## 任务二：实现 BUG-20260203-001（session_start 功能）

### 问题描述

在 v2.2.0 需求中有 "session_start" 功能（FR-MEMORY-003），但从未实现。Agent 在新会话开始时不知道 oc-collab 的存在。

### 需求文档

详见 MEMO-2026-02-004 第 5.1-5.3 节。

### 实现要求

| 组件 | 实现内容 |
|------|----------|
| src/cli/main.py | 添加 `welcome` 命令 |
| src/core/session_manager.py | 新建会话管理器 |
| state/project_state.yaml | 添加 session_start 配置 |
| tests/ | 添加对应测试 |

### 验收标准

| 验证项 | 方法 |
|--------|------|
| Agent 切换后显示欢迎信息 | `oc-collab switch 2` 检查输出 |
| 显示当前 Agent 职责 | 检查输出是否包含职责说明 |
| 显示待办事项 | 检查输出是否包含待办列表 |
| 显示上次遗留问题 | 检查输出是否包含遗留问题 |

### 行动

```bash
# 1. 创建需求文档
cat > docs/01-requirements/requirements_bugfix_20260203_001.md << 'EOF'
# BUGFIX 需求：session_start 功能实现

**Bug ID**: BUG-20260203-001
**严重程度**: P0
**状态**: 待实现
EOF

# 2. 创建设计文档
cat > docs/02-design/detailed_design_session_start_v1.md << 'EOF'
# 详细设计：session_start 功能
EOF

# 3. 开发实现
# (在此处添加代码实现)

# 4. 编写测试
# (在此处添加测试代码)

# 5. 提交
git add docs/01-requirements/ docs/02-design/ src/ tests/
git commit -m "feat: Implement session_start feature - BUG-20260203-001"
git push
```

---

## 任务三：实现动态 Checklist 机制（可选，优先级较低）

### 问题描述

当前评审使用静态 checklist，无法根据文档内容生成针对性检查项。

### 需求文档

详见 MEMO-2026-02-004-ADDENDUM_Dynamic_Checklist.md。

### 实现要求

| 组件 | 实现内容 |
|------|----------|
| src/core/checklist_generator.py | 新建动态 checklist 生成器 |
| src/cli/main.py | 修改 `review` 命令，添加 `--checklist` 选项 |

### 行动

```bash
# 1. 创建设计文档
cat > docs/02-design/detailed_design_dynamic_checklist_v1.md << 'EOF'
# 详细设计：动态 Checklist 机制
EOF

# 2. 开发实现
# (在此处添加代码实现)

# 3. 编写测试
# (在此处添加测试代码)

# 4. 提交
git add docs/ src/ tests/
git commit -m "feat: Add dynamic checklist mechanism for reviews"
git push
```

---

## 任务清单速查

| 任务 | 优先级 | 状态 | 说明 |
|------|--------|------|------|
| 评审 MEMO-2026-02-004 | P0 | 待执行 | 请先阅读并签署 |
| 实现 session_start | P0 | 待执行 | BUG-20260203-001 |
| 实现动态 checklist | P2 | 可选 | 优先级较低 |

---

## 下一步

1. 执行 `git pull` 获取最新文档
2. 阅读 MEMO-2026-02-004
3. 创建评审意见并提交
4. 开始实现 session_start 功能

---

**文档版本**: v1
**创建日期**: 2026-02-03
**状态**: 待执行

---

*如有疑问，请在当前会话中提出。*
