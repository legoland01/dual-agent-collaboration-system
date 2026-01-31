# 详细设计文档：Agent 自动执行功能

## 文档信息

| 项目 | 内容 |
|------|------|
| 设计ID | DES-AGENT-AUTO-001 |
| 需求ID | REQ-AGENT-AUTO-001 |
| 版本 | v1 |
| 状态 | 待评审 |
| 创建日期 | 2026-01-31 |

## 1. 系统架构

### 1.1 组件图

```
┌─────────────────────────────────────────────────────────────┐
│              Agent 自动执行系统                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌─────────────────────┐     ┌─────────────────────┐       │
│   │  agent_auto_runner  │────▶│    oc-collab auto   │       │
│   │      (守护进程)      │     │      (命令)         │       │
│   └──────────┬──────────┘     └─────────────────────┘       │
│              │                                                 │
│              ▼                                                 │
│   ┌─────────────────────┐                                    │
│   │     日志系统         │                                    │
│   │  /tmp/agent_auto.log │                                    │
│   └─────────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 类图

```python
class AgentAutoRunner:
    """Agent 自动执行器"""
    
    def __init__(self, project_path: str, poll_interval: int = 120):
        self.project_path = project_path
        self.poll_interval = poll_interval
        self.last_run = None
    
    def run_auto_command() -> bool:
        """执行 oc-collab auto"""
        pass
    
    def check_should_run() -> bool:
        """检查是否应该执行"""
        pass
    
    def run():
        """运行监控循环"""
        pass
```

---

## 2. auto 命令增强设计

### 2.1 命令行参数

```python
@main.command("auto")
@click.option("--max-iterations", "-n", type=int, default=10)
@click.option("--quiet", "-q", is_flag=True, default=False)
@click.option("--force", "-f", is_flag=True, default=False)
def auto_command(max_iterations: int, quiet: bool, force: bool):
    """自动执行当前任务。"""
    pass
```

### 2.2 force 选项实现

```python
# 在 AutoCollaborationEngine.run() 中
if force:
    # 跳过本地变更检查
    pass
else:
    # 原有逻辑
    if self.git_helper.has_local_changes():
        return {"success": False, "error": "存在未提交的本地修改..."}
```

---

## 3. 守护进程设计

### 3.1 功能特性

| 特性 | 实现 |
|------|------|
| PID 管理 | 写入 `/tmp/agent_auto.pid` |
| 日志 | 写入 `/tmp/agent_auto.log` |
| 优雅退出 | Ctrl+C 处理 |
| 可配置间隔 | `--interval` 参数 |

### 3.2 使用示例

```bash
# 启动（每60秒检查一次）
nohup python3 scripts/agent_auto_runner.py \
    --path /path/to/project \
    --interval 60 > /tmp/agent_auto.log 2>&1 &

# 停止
pkill -f agent_auto_runner.py

# 查看状态
cat /tmp/agent_auto.pid
tail -f /tmp/agent_auto.log
```

---

## 4. 测试用例

### 4.1 单元测试

| 测试项 | 输入 | 预期输出 |
|-------|------|---------|
| auto --force | 本地有未提交变更 | 正常执行 |
| auto 无 --force | 本地有未提交变更 | 报错退出 |
| agent_auto_runner 启动 | 有效路径 | PID 文件创建 |
| agent_auto_runner 停止 | 运行中 | PID 文件删除 |

### 4.2 集成测试

| 测试项 | 说明 |
|-------|------|
| 守护进程执行 | 验证 auto 命令被正确调用 |
| 日志输出 | 验证日志正确写入 |

---

## 5. 实施计划

| 阶段 | 任务 | 优先级 |
|------|------|--------|
| 1 | 实现 --force 选项 | P0 |
| 2 | 创建 agent_auto_runner.py | P1 |
| 3 | 编写测试用例 | P1 |
| 4 | 更新文档 | P1 |

---

## 版本历史

| 版本 | 日期 | 作者 | 变更说明 |
|------|------|------|---------|
| v1 | 2026-01-31 | Agent 1 | 初始设计 |
