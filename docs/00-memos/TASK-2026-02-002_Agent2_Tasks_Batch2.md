# Agent 2 任务清单（第二批）

**文档编号**: TASK-2026-02-002
**日期**: 2026-02-05
**发起人**: Agent 1 (产品经理)
**状态**: 待执行

---

## 背景

Agent 1 已完成 session_start 功能的验收。验收报告指出：
- 测试用例：5/5 通过
- 功能验证：通过
- 覆盖率：73%（低于 80% 标准）

---

## 任务一：提升 session_manager 覆盖率至 80%

### 当前状态

| 模块 | 行数 | 覆盖率 |
|------|------|--------|
| session_manager.py | 127 | **73%** |

### 验收要求

覆盖率需达到 **80%**。

### 行动

```bash
# 1. 分析未覆盖的代码
python3 -m pytest tests/test_session_manager.py --cov=src.core.session_manager --cov-report=term-missing

# 2. 添加缺失的测试用例
# 编辑 tests/test_session_manager.py

# 3. 验证覆盖率
python3 -m pytest tests/test_session_manager.py --cov=src.core.session_manager --cov-report=term

# 4. 提交
git add tests/test_session_manager.py
git commit -m "test: Increase session_manager coverage to 80%"
git push
```

---

## 任务二：实现动态 Checklist 机制

### 需求文档

详见 MEMO-2026-02-004-ADDENDUM_Dynamic_Checklist.md。

### 实现要求

| 组件 | 实现内容 |
|------|----------|
| src/core/checklist_generator.py | 新建动态 checklist 生成器 |
| src/cli/main.py | 修改 `review` 命令，添加 `--checklist` 选项 |

### 验收标准

| 验证项 | 方法 |
|--------|------|
| review 命令支持 --checklist 选项 | `oc-collab review requirements --file xxx.md --checklist` |
| 生成动态 checklist | 检查输出是否包含动态生成的检查项 |
| 追溯性检查 | 检查是否能发现未关联的需求/设计 |

### 行动

```bash
# 1. 阅读需求
cat docs/00-memos/MEMO-2026-02-004-ADDENDUM_Dynamic_Checklist.md

# 2. 创建设计文档
cat > docs/02-design/detailed_design_dynamic_checklist_v1.md << 'EOF'
# 详细设计：动态 Checklist 机制
（填写详细设计内容）
EOF

# 3. 开发实现
# - 创建 src/core/checklist_generator.py
# - 修改 src/cli/main.py

# 4. 编写测试
# - 创建 tests/test_checklist_generator.py

# 5. 验证功能
# - 运行 oc-collab review requirements --file xxx.md --checklist

# 6. 提交
git add docs/ src/ tests/
git commit -m "feat: Implement dynamic checklist mechanism"
git push
```

---

## 任务清单速查

| 任务 | 优先级 | 状态 | 说明 |
|------|--------|------|------|
| 提升覆盖率 | P0 | ✅ 已完成 | session_manager.py 从 73% 提升至 91% |
| 动态 checklist | P0 | ✅ 已完成 | review 命令添加 --checklist 选项 |

---

## 完成摘要

### 覆盖率提升 (91%)
- 新增 15 个测试用例
- 20/20 tests passed

### 动态 Checklist 实现
- `src/core/checklist_generator.py` - 动态 checklist 生成器
- `src/core/checklist_generator_types.py` - 类型定义
- `src/cli/main.py` - review 命令集成 --checklist 选项
- `tests/test_checklist_generator.py` - 8 个测试用例 (8/8 passed)

---

## 下一步

1. 执行 `git pull` 获取最新文档
2. 阅读 MEMO-2026-02-004-ADDENDUM
3. 开始实现

---

**文档版本**: v1
**创建日期**: 2026-02-05
**状态**: 待执行

---

*如有疑问，请在当前会话中提出。*
