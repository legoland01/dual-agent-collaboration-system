# OC-Collab Bug管理指南

## 快速参考

### Bug处理流程

```
发现 → 报告 → 分配 → 调查 → 修复 → 合并 → 发布
```

### Bug严重程度

| 等级 | 定义 | 响应时间 | 示例 |
|------|------|----------|------|
| **P0** | 阻塞协作流程 | 立即修复 | TODO不同步、签署失效 |
| **P1** | 影响功能使用 | 本次会话 | 命令参数错误 |
| **P2** | 轻微问题 | 下个版本 | 文案错误 |
| **P3** | 建议改进 | 可推迟 | 体验优化 |

---

## Bug发现环节

### 什么时候应该发现Bug？

| 场景 | 行为 |
|------|------|
| 测试失败 | 记录测试输出，分析失败原因 |
| 协作不顺畅 | 发现流程断点 |
| 工具返回异常 | 检查错误信息 |
| 跨会话丢失数据 | 追踪数据流向 |

### Bug发现检查清单

```bash
# 发现Bug后立即确认：
1. ✅ 是否可复现？
2. ✅ 影响范围？
3. ✅ 严重程度？
4. ✅ 关联文档？
```

---

## Bug报告环节

### Bug报告模板

```markdown
# Bug 报告：简明标题

**Bug ID**: BUG-YYYYMMDD-XXX
**严重程度**: P0/P1/P2/P3
**状态**: 待修复/修复中/已修复
**发现人**: Agent X
**发现日期**: YYYY-MM-DD

---

## Bug描述

### 表现形式

| 场景 | 问题 |
|------|------|
| xxx | xxx |

### 重现场景

```bash
# 复现步骤
$ 命令
结果
```

### 影响范围

| 影响 | 严重程度 |
|------|----------|
| xxx | P0 |

---

## 问题分析

### 现象分类

| 创建方式 | 是否正常 |
|----------|----------|
| xxx | ✅/❌ |

### 相关文件

| 文件 | 用途 | 状态 |
|------|------|------|
| xxx | xxx | 正常/异常 |

### 关键线索

1. xxx
2. xxx

---

## AgentX 调查方向

### 1. 调查步骤

```bash
# 步骤1: 检查相关文件
cat xxx

# 步骤2: 检查代码实现
cat src/xxx.py

# 步骤3: 对比预期行为
```

### 2. 调查结论

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| xxx | xxx | xxx |

---

## 临时解决方案

```bash
# 手动绕过Bug的方法
xxx
```

---

## 根本解决方案

| 方案 | 说明 | 工时 |
|------|------|------|
| 方案A | xxx | Xh |
| 方案B | xxx | Yh |

---

## 时间线

| 日期 | 事件 |
|------|------|
| YYYY-MM-DD | Agent X 发现问题，创建Bug报告 |
| YYYY-MM-DD | Agent Y 调查 |
| YYYY-MM-DD | Agent Y 修复 |
| YYYY-MM-DD | 合并到主分支 |
| YYYY-MM-DD | 发布Patch |

---

## 关联文档

| 文档 | 说明 |
|------|------|
| xxx | xxx |

---

**创建人**: Agent X
**日期**: YYYY-MM-DD
**状态**: 待修复
```

### Bug报告存放位置

```
docs/00-memos/BUG-YYYYMMDD-XXX_简短描述.md
```

### Bug ID命名规范

```
BUG-YYYYMMDD-XXX
- YYYYMMDD: 发现日期
- XXX: 序号（001开始）
```

---

## Bug分配环节

### TODO分配规则

```yaml
todos:
  - id: "TODO-BUG-XXX"
    content: "修复 BUG-YYYYMMDD-XXX: 简明标题"
    from: "agent1"        # 发现者
    to: "agent2"          # 修复者
    phase: "bugfix"
    priority: "P0/P1/P2"
    bug_id: "BUG-YYYYMMDD-XXX"
    status: "pending"     # pending/in_progress/completed
    created_at: "timestamp"
```

### 分配检查清单

```bash
# 分配Bug后必须：
1. ✅ 创建TODO任务
2. ✅ 指定 from（发现人）
3. ✅ 指定 to（修复者）
4. ✅ 指定 priority（严重程度）
5. ✅ 关联 Bug ID
```

### 分配规则

| Bug严重程度 | 谁修复 | 响应时间 |
|-------------|--------|----------|
| P0 | 任何人 | 立即 |
| P1 | 相关Agent | 本次会话 |
| P2/P3 | 相关Agent | 下个版本 |

---

## Bug调查环节

### 调查步骤

```bash
# 步骤1: 阅读Bug报告
cat docs/00-memos/BUG-YYYYMMDD-XXX.md

# 步骤2: 复现Bug
# 按照报告中的重现场景操作

# 步骤3: 分析代码
# 检查相关文件

# 步骤4: 定位根因
# 找到问题的根本原因

# 步骤5: 提出解决方案
# 提出修复方案
```

### 调查结论模板

```markdown
## 调查结论

### 根因分析

| 问题 | 原因 | 层级 |
|------|------|------|
| xxx | xxx | 代码/流程/文档 |

### 解决方案

| 方案 | 说明 | 推荐 |
|------|------|------|
| 方案A | xxx | ✅ |
| 方案B | xxx | ❌ |
```

### 调查检查清单

```bash
# 调查完成后必须：
1. ✅ 复现Bug
2. ✅ 定位根因
3. ✅ 提出解决方案
4. ✅ 记录到Bug报告
```

---

## Bug修复环节

### 修复步骤

```bash
# 步骤1: 创建修复分支
git checkout -b fix/BUG-YYYYMMDD-XXX

# 步骤2: 修复代码
# 编辑相关文件

# 步骤3: 编写测试
# 确保修复后测试通过

# 步骤4: 提交修复
git add .
git commit -m "fix: 修复 BUG-YYYYMMDD-XXX (简明描述)"

# 步骤5: 创建Pull Request
```

### 修复提交规范

```bash
# 修复提交消息
fix(BUG-YYYYMMDD-XXX): 简明描述

[body]
- 问题描述
- 修复方案
- 测试结果

[footer]
Closes #BUG-YYYYMMDD-XXX
```

### 修复检查清单

```bash
# 修复完成后必须：
1. ✅ 测试通过
2. ✅ 代码审查通过
3. ✅ 提交信息规范
4. ✅ 更新Bug报告状态
```

---

## Bug合并与发布环节

### 合并规则

| Bug严重程度 | 合并时机 |
|-------------|----------|
| P0 | 立即合并 |
| P1 | 本次会话结束前 |
| P2/P3 | 版本发布时 |

### Patch版本规范

```
# Patch版本号规则
v2.2.X.Y
- X: 功能版本
- Y: Patch版本（从1开始）

# Patch发布时机
- P0 Bug: 立即发布Patch
- P1 Bug: 功能版本发布时包含
- P2/P3 Bug: 可累积多个后发布
```

### 合并检查清单

```bash
# 合并前必须：
1. ✅ 所有测试通过
2. ✅ 代码审查通过
3. ✅ 更新CHANGELOG.md
4. ✅ 更新版本号
```

---

## Bug闭环环节

### 关闭Bug

```markdown
# 在Bug报告中更新

## 时间线

| 日期 | 事件 |
|------|------|
| YYYY-MM-DD | Agent X 发现问题，创建Bug报告 |
| YYYY-MM-DD | Agent Y 调查并修复 |
| YYYY-MM-DD | 合并到主分支 |
| YYYY-MM-DD | 发布Patch vX.X.X-Y ✅ 已关闭 |

---

**状态**: 已修复 ✅
**修复版本**: vX.X.X-Y
```

### 经验总结

```markdown
## 教训总结

| 教训 | 说明 |
|------|------|
| xxx | xxx |

## 防止措施

| 措施 | 说明 |
|------|------|
| xxx | xxx |

## 是否应纳入Skill？

- [ ] 是 → 更新/创建相关Skill
- [ ] 否 → 仅记录
```

---

## 常见错误与正确做法

| 错误做法 | 正确做法 |
|----------|----------|
| 发现Bug不创建报告 | 立即创建Bug报告 |
| Bug报告不完整 | 按模板填写所有字段 |
| 不分配TODO任务 | 必须创建TODO分配给修复者 |
| 修复后不更新报告 | 及时更新Bug报告状态 |
| 不记录教训 | 总结教训并考虑纳入Skill |

---

## Git 提交规范 ⭐

```bash
# 创建Bug报告
git add docs/00-memos/BUG-YYYYMMDD-XXX.md
git commit -m "docs: 创建 BUG-YYYYMMDD-XXX (简明描述)"

# 修复Bug
git add src/ tests/
git commit -m "fix: 修复 BUG-YYYYMMDD-XXX (简明描述)"

# 合并修复
git checkout main
git merge fix/BUG-YYYYMMDD-XXX
git commit -m "merge: 合并 BUG-YYYYMMDD-XXX 修复"

# 发布Patch
git tag vX.X.X-Y
```

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-08 | 初始版本 |
