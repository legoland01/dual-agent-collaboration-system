# OC-Collab 测试验收指南

## 快速参考

### 角色分工

| 角色 | 必须做 | 禁止做 |
|------|--------|--------|
| **Agent 1** | 黑盒测试、验收签署、准备测试用例 | 代码实现、白盒测试 |
| **Agent 2** | 代码实现、白盒测试、开发签署 | 黑盒测试、签署"验收通过" |

### 测试时机

```
需求: APPROVED ✅
设计: APPROVED ✅
开发: ⏳ pending → ✅ completed  ← ← ← 此时才能开始测试！
测试: ⏳ pending
验收: ⏳ pending
```

---

## 测试前检查清单

### 1. 开发状态检查 ⭐

**在运行任何测试前，必须确认：**

```
bash
# 1. 确认开发已完成
cat state/project_state.yaml | grep "v2.2.3" -A5

# 应该看到:
#   development:
#     status: completed  # 而不是 pending
```

**禁止**: 开发状态为 pending 时运行测试

### 2. 代码提交检查

```bash
# 1. 确认所有代码已提交
git status

# 2. 确认有开发完成的commit
git log --oneline -5

# 3. 确认模块文件存在
ls -la src/core/
# 应该看到:
#   - context_manager.py
#   - todo_sync_manager.py
```

**禁止**: 有未提交的代码时运行测试

### 3. 版本核对

```bash
# 1. 确认测试文件版本与开发版本一致
grep "v2.2.3" tests/test_v2_2_3.py

# 2. 确认设计文档版本
grep "版本.*2.2.3" docs/02-design/DETAIL-*.md

# 3. 核对需求版本
grep "v2.2.3" docs/01-requirements/requirements_v2.2.3_READY.md
```

### 4. 环境准备

```bash
# 1. 拉取最新代码（如果有远程更新）
git pull

# 2. 确认依赖已安装
pip install -e .

# 3. 清除旧缓存
rm -rf .pytest_cache __pycache__ src/*/__pycache__
```

---

## 测试准备流程

### Agent 1 的测试准备工作

| 步骤 | 操作 | 状态 |
|------|------|------|
| 1 | 阅读设计文档，理解模块接口 | ☐ |
| 2 | 编写/完善测试用例 | ☐ |
| 3 | 确认开发状态为 completed | ☐ |
| 4 | 确认代码已提交 | ☐ |
| 5 | 核对版本号一致 | ☐ |
| 6 | 运行测试 | ☐ |
| 7 | 签署验收 | ☐ |

### 测试用例来源

1. **设计文档中的测试用例清单**
   - 位置: `docs/02-design/DETAIL-*.md` → `## 4. 测试设计`
   
2. **已有测试文件**
   - 位置: `tests/test_v2_2_3.py`
   
3. **黑盒测试用例模板**
   - 位置: `docs/03-test/blackbox_test_cases_TEMPLATE.md`

---

## 测试执行规范

### 运行测试

```bash
# 运行特定版本测试
python -m pytest tests/test_v2_2_3.py -v

# 运行所有测试（回归测试）
python -m pytest tests/ -v --tb=short

# 运行黑盒测试
python -m pytest tests/test_blackbox_*.py -v
```

### 测试结果记录

| 结果类型 | 处理方式 |
|----------|----------|
| ✅ 全部通过 | 签署验收，更新状态 |
| ⚠️ 部分失败 | 记录问题，要求Agent2修复 |
| ❌ 全部失败 | 检查环境，报告Bug |

---

## 验收签署

### 签署内容模板

```
验收结果: ✅ 通过

测试执行:
- 测试文件: tests/test_v2_2_3.py
- 测试命令: python -m pytest tests/test_v2_2_3.py -v
- 测试结果: XX passed, YY failed

问题记录:
- [P0]: xxx
- [P1]: xxx

签署: Agent 1 @ 2026-02-08
```

### 签署规范

| 角色 | 正确的签署内容 |
|------|---------------|
| Agent 1 | "测试验收通过" / "验收通过" |
| Agent 2 | "开发完成" / "测试环境就绪" |

---

## 常见错误

| 错误 | 正确做法 |
|------|---------|
| 开发pending时运行测试 | 等待开发状态变为completed |
| 不检查git status直接测试 | 先确认代码已提交 |
| 不核对版本号 | 确认测试文件与开发版本一致 |
| 测试失败直接签署 | 必须记录问题，要求修复 |
| Agent1做白盒测试 | 白盒测试由Agent2执行 |

---

## Git 提交规范 ⭐

**测试完成后，必须提交测试报告**

```bash
# 1. 提交测试用例更新
git add tests/
git commit -m "test: 更新 v2.2.3 测试用例"

# 2. 验收通过后，提交验收报告
git add docs/03-test/
git commit -m "docs: v2.2.3 测试验收通过"
```

**禁止**: 测试完成后不提交，积压多个提交

---

## 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| v1 | 2026-02-08 | 初始版本 |
| v2 | 2026-02-08 | 添加测试前检查清单，强调开发状态检查 |
