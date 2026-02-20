# v2.3.2 开发Compaction文档

**日期**: 2026-02-18  
**版本**: v2.3.2  
**状态**: 开发中

---

## 一、项目目标

实现TODO存储SQLite迁移 + 监听守护进程 + 实时通知和Question窗口交互

---

## 二、已完成工作

### 2.1 SQLite迁移

| 模块 | 文件 | 状态 |
|------|------|------|
| TODO存储 | todo_sync_manager.py | ✅ 完成 |
| 队列管理 | todo_queue_manager.py | ✅ 完成 |
| 会话管理 | session_manager.py | ✅ 完成 |
| 冲突检测 | conflict_detector.py | ✅ 完成 |
| 上下文传递 | context_carrier.py | ✅ 完成 |
| ACK确认 | ack_confirm.py | ✅ 完成 |

### 2.2 CLI Bug修复 (5个)

| Bug | 描述 | 状态 |
|-----|------|------|
| 1 | todo complete参数错误 | ✅ 已修复 |
| 2 | todo ack不更新数据库 | ✅ 已修复 |
| 3 | todo mark-read不更新数据库 | ✅ 已修复 |
| 4 | todowrite --source不生效 | ✅ 已修复 |
| 5 | config set嵌套字典报错 | ✅ 已修复 |

### 2.3 测试验证

- **单元测试**: 94个测试通过
- **E2E测试**: 102个测试通过
- **新增测试**: test_instruction_file_generation

### 2.4 Question窗口通知 (BUG-20260218-003)

**问题根源**: OpenCode需要加载instruction文件才能让LLM知道要调用question tool

**解决方案**:
1. `online_puller.py` 同步更新3个位置的instruction文件:
   - `config/instructions/TODO_NOTIFY.md`
   - `opencode_src/instructions/TODO_NOTIFY.md`
   - `instructions/TODO_NOTIFY.md` (项目根目录)

2. 配置文件:
   - `opencode.json` - 放在项目根目录，配置加载instructions
   - `instructions/TODO_NOTIFY.md` - 通知规则

**触发流程**:
```
1. agent listen 检测到新TODO
2. notify_user() 更新 instruction 文件
3. 用户启动OpenCode (从项目根目录)
4. 用户告诉LLM: "查看TODO"
5. LLM读取instruction → 调用question tool → 弹出窗口
```

---

## 三、当前问题

### 已解决

- ✅ Instruction文件生成和同步
- ✅ macOS系统通知（测试中已成功多次）
- ✅ agent listen轮询检测

### 待验证

- ⏳ **Question窗口弹出**:刚把配置文件复制到项目根目录，需要重启OpenCode验证

---

## 四、待办任务

| ID | 内容 | 优先级 | 状态 |
|----|------|--------|------|
| TODO-1to2-004 | 修复BUG-20260218-003: Question窗口通知和交互 | high | 进行中 |

---

## 五、下一步行动

1. **用户重启OpenCode** (从项目根目录)
2. **测试Question窗口**: 告诉LLM "查看TODO"
3. **验证结果**: 确认是否弹出Question窗口

---

## 六、关键文件

| 文件 | 作用 |
|------|------|
| src/core/online_puller.py | 更新instruction文件 |
| opencode.json | OpenCode配置(加载instructions) |
| instructions/TODO_NOTIFY.md | 通知规则 |
| tests/test_v2_3_2_modules.py | 单元测试 |
| tests/test_v232_e2e.py | E2E测试 |
| docs/00-memos/BUG-20260218-003_*.md | Bug报告 |
| docs/00-memos/POC_OpenCode_TUI_*.md | POC研究 |

---

## 七、测试命令

```bash
# 单元测试
pytest tests/test_v2_3_2_modules.py::TestOnlinePuller -v

# E2E测试
pytest tests/test_v232_e2e.py -k "notify or agent_listen" -v
```

---

**下一步**: 用户重启OpenCode后验证Question窗口是否弹出
