# Skill行为测试计划

**版本**: v1
**日期**: 2026-02-10
**测试目标**: 验证系统运行时正确调用skill片段

---

## 1. 测试范围

| 模块 | 测试内容 |
|------|----------|
| F-AI (auto_checker) | 协作规范自动检查 |
| F-CONTEXT (context_carrier) | 上下文携带和传递 |
| F-CONFLICT (conflict_detector) | Agent行为冲突检测 |
| F-SKILL (skill_searcher/slicer/enforcer) | Skill动态切片和强制执行 |

---

## 2. 测试场景设计

### 2.1 F-AI 自动检查器测试场景

| 场景编号 | 场景描述 | 预期行为 |
|----------|----------|----------|
| F-AI-001 | Agent1尝试创建代码文件 | 系统应拒绝/警告 |
| F-AI-002 | Agent2尝试修改需求文档 | 系统应拒绝/警告 |
| F-AI-003 | Agent尝试跳过需求分析直接创建需求文档 | 系统应触发需求分析skill |
| F-AI-004 | 新会话开始 | 系统应自动加载协作规则 |
| F-AI-005 | 文档状态不符合规范时操作 | 系统应检查状态并警告 |

**预期调用的Skill片段**:
- `oc_collab_collaboration_guide` - 角色权限检查
- `oc_collab_requirements_guide` - 需求分析检查

### 2.2 F-CONTEXT 上下文携带测试场景

| 场景编号 | 场景描述 | 预期行为 |
|----------|----------|----------|
| F-CTX-001 | 会话切换时 | 应携带当前阶段信息 |
| F-CTX-002 | Agent交接时 | 应传递待办状态 |
| F-CTX-003 | 跨会话操作 | 应保持上下文一致性 |

**预期调用的Skill片段**:
- `oc_collab_collaboration_guide` - 会话管理规则

### 2.3 F-CONFLICT 冲突检测测试场景

| 场景编号 | 场景描述 | 预期行为 |
|----------|----------|----------|
| F-CNF-001 | Agent1签署"评审通过" | 系统应检测到角色越权 |
| F-CNF-002 | Agent签署自己创建的文档 | 系统应检测到重复签署 |
| F-CNF-003 | Agent执行角色禁止的操作 | 系统应检测并阻止 |

**预期调用的Skill片段**:
- `oc_collab_requirements_review_guide` - 签署规则检查

### 2.4 F-SKILL 动态切片测试场景

| 场景编号 | 场景描述 | 预期行为 |
|----------|----------|----------|
| F-SKL-001 | 用户询问"如何写需求" | 应切片需求指南相关内容 |
| F-SKL-002 | 用户询问"如何部署" | 应切片部署指南相关内容 |
| F-SKL-003 | 用户询问"发现Bug怎么办" | 应切片Bug管理指南相关内容 |
| F-SKL-004 | 用户要求强制执行Skill | 应执行skill enforce命令 |
| F-SKL-005 | 搜索Skill时 | 应返回相关Skill列表 |

---

## 3. 测试方法

### 3.1 CLI命令测试

通过直接调用CLI命令验证F-SKILL功能：

```bash
# 测试skill search
oc-collab skill search --keywords "需求"

# 测试skill slice
oc-collab skill slice oc_collab_requirements_guide

# 测试skill enforce
oc-collab skill enforce
```

### 3.2 系统行为日志分析

通过分析系统日志验证F-AI/F-CONTEXT/F-CONFLICT：

1. 启用详细日志模式
2. 执行测试操作
3. 分析日志中的Skill调用记录

### 3.3 模拟Agent对话测试

创建模拟对话，验证系统响应：

```
User: "我需要创建一个新的需求文档"
Expected: 系统应提供需求模板，并提醒先做需求分析

User: "Agent2来评审这个需求"
Expected: 系统应触发评审流程
```

---

## 4. 测试用例详细设计

### F-AI-001: Agent1创建代码文件测试

**场景**: Agent1尝试在src/目录下创建文件

**预期行为**:
1. 系统应检测到Agent1无src/权限
2. 应返回权限错误或警告
3. 可能触发`oc_collab_collaboration_guide`中的权限规则

**测试步骤**:
```bash
# 1. 模拟Agent1身份
# 2. 尝试创建 src/test_ai.py
# 3. 检查系统响应
```

### F-AI-003: 跳过需求分析检测测试

**场景**: Agent直接创建需求文档而未做需求分析

**预期行为**:
1. 系统应检测到缺少需求分析环节
2. 应提示先做需求分析
3. 应提供`oc_collab_requirements_guide`相关内容

**测试步骤**:
```bash
# 1. 直接创建需求文档（无ANALYSIS文件）
# 2. 检查系统是否提示先做需求分析
```

### F-SKL-001: Skill切片测试 - 需求场景

**场景**: 用户询问如何编写需求文档

**测试步骤**:
```bash
oc-collab skill search --keywords "需求 模板"
oc-collab skill slice oc_collab_requirements_guide --section "标准文档结构"
```

**验证点**:
- 返回的切片是否包含"标准文档结构"章节
- 返回内容是否与原skill一致

### F-SKL-005: Skill搜索测试

**场景**: 搜索包含特定关键词的Skill

| 关键词 | 预期返回Skill |
|--------|---------------|
| 需求 | oc_collab_requirements_guide |
| 评审 | oc_collab_requirements_review_guide |
| 设计 | oc_collab_outline_design_guide, oc_collab_detailed_design_guide |
| Bug | oc_collab_bug_management_guide |
| 部署 | oc_collab_deployment_guide |

---

## 5. 测试执行计划

### 阶段1: CLI命令测试 (F-SKL系列)

1. 执行所有skill search命令
2. 执行所有skill slice命令
3. 执行skill enforce命令
4. 记录返回结果

### 阶段2: 行为日志分析 (F-AI/F-CTX/F-CNF系列)

1. 启用debug日志
2. 执行权限操作测试
3. 分析日志输出
4. 验证Skill调用

### 阶段3: 模拟对话测试

1. 编写模拟对话脚本
2. 执行对话测试
3. 验证系统响应

---

## 6. 预期结果

| 测试类型 | 通过标准 |
|----------|----------|
| CLI命令测试 | 所有命令返回码为0 |
| 行为日志分析 | 日志中包含正确的Skill调用记录 |
| 模拟对话测试 | 系统响应符合Skill预期 |

---

## 7. 后续工作

测试完成后，需要：
1. 分析测试失败原因
2. 修复系统bug
3. 更新Skill文档
4. 迭代优化测试用例

---

**作者**: Agent 1
**版本**: v1
**更新日期**: 2026-02-10
