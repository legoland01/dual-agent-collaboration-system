# v2.2.6 黑盒测试用例

**版本**: v1.0
**日期**: 2026-02-09
**作者**: Agent 1 (产品经理)
**关联需求**: requirements_v2.2.6.md

---

## 测试范围

| 功能模块 | 测试类型 | 说明 |
|----------|----------|------|
| F-AI: 智能TODO系统 | CLI黑盒测试 | todowrite参数检查、上下文携带、冲突检测 |
| F-SKILL: Skill检索增强 | CLI黑盒测试 | skill search/slice/enforce命令 |

---

## 测试环境准备

```bash
# 1. 安装最新版本
pip install -e .

# 2. 清除缓存
rm -rf .pytest_cache __pycache__ src/*/__pycache__

# 3. 确认版本
oc-collab .a
```

---

## 测试用例

### F-AI-001: todowrite参数自动检查

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-AI-001 | 无参数执行todowrite | - | `oc-collab todowrite` | 显示参数缺失提示 |
| BB-AI-002 | 缺少--content | - | `oc-collab todowrite --agent 1` | 提示--content必填 |
| BB-AI-003 | 缺少--agent | - | `oc-collab todowrite --content "test"` | 提示--agent必填 |
| BB-AI-004 | 无效agent_id | - | `oc-collab todowrite --content "test" --agent 3` | 提示agent_id无效 |
| BB-AI-005 | 有效完整参数 | - | `oc-collab todowrite --content "黑盒测试" --agent 1 --priority high` | 成功创建TODO |
| BB-AI-006 | 默认priority | - | `oc-collab todowrite --content "测试默认" --agent 1` | priority默认为P1 |

### F-AI-002: TODO上下文携带

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-AI-007 | 创建时关联历史 | 存在历史TODO | 创建新TODO | 输出包含历史TODO摘要 |
| BB-AI-008 | 记录版本信息 | - | 创建TODO | 记录当前版本号 |
| BB-AI-009 | 生成上下文摘要 | - | 创建TODO | 输出上下文摘要 |

### F-AI-003: 冲突检测

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-AI-010 | 检测重复内容 | 存在相同内容TODO | 创建重复TODO | 提示重复警告 |
| BB-AI-011 | 检测优先级冲突 | 存在5个相同优先级TODO | 创建新TODO | 提示优先级冲突 |
| BB-AI-012 | 正常创建无冲突 | 无冲突 | 创建TODO | 成功创建，无冲突提示 |

### F-SKILL-001: Skill关键词检索

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-SKILL-001 | 搜索存在的关键词 | skills存在 | `oc-collab skill search --keywords todowrite` | 显示匹配结果 |
| BB-SKILL-002 | 搜索不存在的关键词 | skills存在 | `oc-collab skill search --keywords nonexistent` | 显示未找到 |
| BB-SKILL-003 | 多关键词搜索 | skills存在 | `oc-collab skill search --keywords "todowrite requirements"` | 显示多关键词匹配 |
| BB-SKILL-004 | 搜索结果排序 | skills存在 | 执行搜索 | 结果按相关性排序 |

### F-SKILL-002: Skill切片机制

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-SKILL-005 | 列出章节 | skill存在 | `oc-collab skill slice --list` | 显示所有章节 |
| BB-SKILL-006 | 查看特定章节 | skill存在 | `oc-collab skill slice --chapter 2` | 显示章节内容 |
| BB-SKILL-007 | 查看子章节 | skill存在 | `oc-collab skill slice --chapter 2.1` | 显示子章节内容 |

### F-SKILL-003: Skill强制查找增强

| 用例ID | 测试场景 | 前置条件 | 测试步骤 | 预期结果 |
|--------|----------|----------|----------|----------|
| BB-SKILL-008 | 检测缺失的Skill | 某些skill缺失 | `oc-collab skill enforce` | 显示缺失skill列表 |
| BB-SKILL-009 | todowrite前检查 | - | 执行todowrite | 自动检查并提示相关skill |
| BB-SKILL-010 | 多个行动类型 | - | 测试不同命令 | 正确映射对应skill |

---

## 测试执行

### 执行命令

```bash
# 执行所有黑盒测试
python -m pytest tests/test_blackbox_v226.py -v

# 执行单个测试
python -m pytest tests/test_blackbox_v226.py::TestTODOWriteAutoCheck -v
python -m pytest tests/test_blackbox_v226.py::TestSkillSearch -v
```

### 测试结果记录

| 测试组 | 用例数 | 通过 | 失败 | 通过率 |
|--------|--------|------|------|--------|
| F-AI-001 | 6 | | | |
| F-AI-002 | 3 | | | |
| F-AI-003 | 3 | | | |
| F-SKILL-001 | 4 | | | |
| F-SKILL-002 | 3 | | | |
| F-SKILL-003 | 3 | | | |
| **合计** | **22** | | | |

---

## 验收结论

| 条件 | 状态 |
|------|------|
| 所有黑盒测试通过 | ☐ |
| CLI命令功能正常 | ☐ |
| 无严重Bug | ☐ |

---

**创建人**: Agent 1
**日期**: 2026-02-09
**状态**: DRAFT
