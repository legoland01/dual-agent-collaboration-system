# BUG-20260215-009: 缺少启动时自动检测并升级机制

**BUG编号**：BUG-20260215-009
**发现日期**：2026-02-15
**发现者**：Agent 1
**优先级**：P1
**状态**：open

---

## 问题描述

v2.2.12.1 已发布多日，但用户仍在使用旧版本，原因是：
1. 用户没有开新终端窗口的习惯
2. 每次发布的修复用户都没用到

### 影响

| 发布版本 | 用户是否用到 |
|---------|------------|
| v2.2.12 StateReceiver CLI | ❌ 未用到 |
| v2.2.12 todowrite 参数修复 | ❌ 未用到 |
| v2.2.12.1 AutoBugDetector 集成 | ❌ 未用到 |

---

## 根因分析

### 当前行为

```bash
$ oc-collab --version
# 使用的是 pip install -e . 时的代码
# 不是最新发布版本
```

### 期望行为

```bash
$ oc-collab status
🔄 检测到新版本 v2.2.12.1，正在升级...
✅ 已升级，请新开终端窗口使用

$ oc-collab status
✅ 当前已是最新版本 v2.2.12.1
```

---

## 修复方案

在 `oc-collab` 启动时自动检测并升级：

```python
# src/cli/auto_upgrade.py

def check_and_upgrade():
    """检测当前版本与PyPI版本，如需要则升级"""
    current = get_current_version()
    latest = get_latest_from_pypi()

    if current < latest:
        if confirm_upgrade():
            subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "opencode-collaboration"])
            print("✅ 已升级，请新开终端窗口使用")
            sys.exit(0)
```

在 `main.py` 入口处调用：

```python
# src/cli/main.py

from .auto_upgrade import check_and_upgrade

if __name__ == "__main__":
    check_and_upgrade()  # 启动时检查并升级
    main()
```

---

## 验收标准

- [ ] `oc-collab status` 自动检测并提示升级
- [ ] 升级后提示"请新开终端窗口使用"
- [ ] 已是最新版本时不提示
- [ ] 网络错误时静默跳过

---

## 关联文档

| 文档 | 说明 |
|------|------|
| BUG-20260215-001 | todowrite 参数传递修复 |
| BUG-20260215-002 | AutoBugDetector CLI 集成 |

---

**报告人**：Agent 1
**日期**：2026-02-15
**状态**：待修复
