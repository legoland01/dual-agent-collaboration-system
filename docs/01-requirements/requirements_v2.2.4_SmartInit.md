# 需求文档：oc-collab init 智能初始化

**需求ID**: REQ-INIT-001
**版本**: v1
**日期**: 2026-02-07
**作者**: Agent 2
**状态**: DRAFT

---

## 1. 问题

### 1.1 当前问题

| 场景 | 问题 |
|------|------|
| 新项目 | 手动创建目录、文件、skills |
| 已有环境 | 用户不知道是否需要重复初始化 |
| 每次启动 | 需要手动打开 OpenCode |

### 1.2 用户痛点

```
用户：我想用 oc-collab，但不知道需要设置什么。
用户：我已经设置过了，不知道能不能再用 init。
```

---

## 2. 解决方案

### 2.1 智能初始化

```bash
oc-collab init
```

**自动检测**：

```
if 项目根目录存在 .a 文件:
    ✅ 已检测到 oc-collab 环境
    ✅ 直接打开 OpenCode（不做任何修改）
else:
    🔧 创建 .a 文件（Agent 规则）
    🔧 创建 docs/ 目录
    🔧 创建 state/ 目录
    ✅ 打开 OpenCode
```

### 2.2 用户操作

**一句话**：

```bash
bash$ oc-collab init
✅ 环境已就绪，OpenCode 已启动
Human: 你是 agent1。
```

### 2.3 创建的文件

| 文件 | 说明 |
|------|------|
| `.a` | Agent 规则文件（AI 会自动读取） |
| `docs/` | 文档目录 |
| `state/` | 状态目录 |

---

## 3. 用户体验

### 3.1 首次使用（新项目）

```bash
bash$ oc-collab init
✅ 已创建 .a 文件
✅ 已创建 docs/ 目录
✅ 已创建 state/ 目录
✅ OpenCode 已启动

Human: 你是 agent1。
```

### 3.2 再次使用（已有环境）

```bash
bash$ oc-collab init
✅ 已检测到 oc-collab 环境，无需修改
✅ OpenCode 已启动

Human: 你是 agent1。
```

---

## 4. 验收标准

- [ ] 检测到 `.a` 文件时，跳过初始化，直接打开 OpenCode
- [ ] 未检测到 `.a` 文件时，自动创建 `.a`, `docs/`, `state/`
- [ ] 初始化后自动打开 OpenCode
- [ ] 不覆盖已有文件

---

## 5. 实现要点

### 5.1 检测逻辑

```python
def check_environment():
    """检查 oc-collab 环境"""
    if (Path.cwd() / ".a").exists():
        return "already_configured"
    return "need_setup"
```

### 5.2 初始化逻辑

```python
def init_project():
    """初始化项目"""
    if check_environment() == "already_configured":
        open_opencode()
        return

    # 创建必要文件
    create_file(".a")
    create_dir("docs/")
    create_dir("state/")

    open_opencode()
```

---

## 6. 工时预估

| 任务 | 工时 |
|------|------|
| 检测逻辑实现 | 1h |
| 初始化逻辑实现 | 1h |
| 单元测试 | 1h |

**总计**: 3h

---

## 7. 依赖

无外部依赖，基于现有 oc-collab CLI 扩展。

---

## 8. 后续扩展（可选）

当前版本只做最简实现，后续可扩展：

- [ ] 支持 `--force` 强制重新初始化
- [ ] 支持 `--type python/java` 指定项目类型
- [ ] 支持 `--template minimal/full` 指定模板

---

## 签署

### Agent 2 提案

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | 2026-02-07 | ✅ |

### Agent 1 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 1 | | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-07
**状态**: DRAFT
