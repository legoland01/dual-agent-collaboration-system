# v2.2.7 - v2.2.12 功能验证BUG汇总

**验证日期**: 2026-02-16
**验证者**: Agent1

---

## BUG列表

### BUG-20260216-007: todowrite生成错误编号

**严重程度**: P0
**状态**: fixed

**问题**: Agent1运行todowrite，生成了`TODO-2-385`而不是`TODO-1-xxx`

**复现**:
```bash
$ oc-collab todowrite --content "测试编号修复"
→ ✅ 待办已创建: [TODO-2-385] 测试编号修复
```

**预期**: Agent1应该生成`TODO-1-xxx`格式

**根因**: Agent上下文无法识别，ContextManager未正确从state文件读取

**修复**:
- enhanced_commands.py: 移除自动从state文件读取agent的逻辑
- context_manager.py: 添加从state/project_state.yaml读取current_agent的fallback
- state_manager.py: set_active_agent方法同步更新current_agent字段

**验证**: ✅ 已修复

---

### BUG-20260216-008: Agent上下文无法识别

**严重程度**: P0
**状态**: fixed

**问题**: 运行任何CLI命令都显示"无法获取Agent上下文"

**复现**:
```bash
$ oc-collab todowrite --content "test"
→ ⚠️ 无法获取Agent上下文，建议先运行 'oc-collab switch 1' 或 'oc-collab switch 2' 切换Agent
```

**影响**: 所有需要Agent上下文的功能都无法正常工作

**修复**:
- context_manager.py: 添加从state/project_state.yaml读取current_agent的fallback逻辑
- state_manager.py: set_active_agent方法同步更新current_agent字段

**验证**: ✅ 已修复

---

### BUG-20260216-009: skill test运行报错

**严重程度**: P0
**状态**: fixed

**问题**: 运行`oc-collab skill test`直接崩溃

**复现**:
```bash
$ oc-collab skill test
→ TypeError: unsupported operand type(s) for /: 'PosixPath' and 'dict'
```

**根因**: skill_tester.py第144行，output是dict类型而不是string

**修复**:
- skill_tester.py: 增强outputs格式处理，支持三种格式：
  1. 简单列表: ["file1", "file2"]
  2. 字典列表: [{"type": "file", "path": "xxx"}, ...]
  3. 字典格式: {"documents": [...], "artifacts": [...]}

**验证**: ✅ 已修复

---

### BUG-20260216-010: deploy full缺少build包

**严重程度**: P1
**状态**: fixed

**问题**: 部署失败，提示缺少build包

**复现**:
```bash
$ oc-collab deploy full
→ 步骤 build 失败: python -m build 命令未找到
```

**根因**: package_builder.py使用`python`命令但系统只有`python3`

**修复**:
- package_builder.py: 使用`sys.executable`获取当前Python解释器路径

**验证**: ✅ 已修复

---

### BUG-20260216-011: skill enforce缺少design skill

**严重程度**: P1
**状态**: fixed

**问题**: 部分Skill缺失

**复现**:
```bash
$ oc-collab skill enforce
→ ❌ design: oc_collab_design_guide
```

**根因**: skill_enforcer.py中design映射到错误的skill名称

**修复**:
- skill_enforcer.py: 将`oc_collab_design_guide`改为`oc_collab_detailed_design_guide`

**验证**: ✅ 已修复

---

### BUG-20260216-012: 测试用例使用错误参数

**严重程度**: P1
**状态**: fixed

**问题**: pytest测试使用`--agent`参数，但CLI不支持

**复现**:
```bash
$ pytest tests/test_todowrite_complete.py
→ FAILED: Error: No such option: --agent
```

**根因**: todowrite命令移除了--agent参数支持

**修复**:
- enhanced_commands.py: 添加--agent参数支持

**验证**: ✅ 已修复

---

### BUG-20260216-013: status显示项目版本错误

**严重程度**: P2
**状态**: not_a_bug

**问题**: 项目版本显示v2.3.0，但实际应该是v2.2.12

**复现**:
```bash
$ oc-collab status
→ 项目名称: oc-collab v2.3.0
→ 当前版本: v2.3.0
```

**分析**: 经核实，project_state.yaml中确实存在v2.3.0版本记录，且存在对应的部署TODO任务。v2.3.0是当前实际版本，非BUG。

**验证**: 不是BUG，状态显示正确

---

## 总结

| BUG ID | 功能 | 问题 | 严重程度 | 状态 |
|--------|------|------|----------|------|
| BUG-007 | todowrite | 生成错误编号 | P0 | fixed |
| BUG-008 | Agent上下文 | 无法识别 | P0 | fixed |
| BUG-009 | skill test | 运行报错 | P0 | fixed |
| BUG-010 | deploy full | 缺少build包 | P1 | fixed |
| BUG-011 | skill enforce | 缺少Skill | P1 | fixed |
| BUG-012 | pytest测试 | 参数错误 | P1 | fixed |
| BUG-013 | status | 版本显示错误 | P2 | not_a_bug |

---

**状态**: open
**创建时间**: 2026-02-16
