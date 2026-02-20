# Agent启动与重机制设计

**日期**: 2026-02-18  
**版本**: v1.0

---

## 一、OpenCode启动方式

### 1.1 CLI命令

```bash
# 基本启动
opencode [project] --prompt "系统提示词"

# 示例
opencode /path/to/金融法院卷宗系统 --prompt "你当前是agent1-001，负责..."
```

### 1.2 关键参数

| 参数 | 说明 |
|------|------|
| `[project]` | 项目目录路径 |
| `--prompt` | 系统提示词 |
| `--continue` / `-c` | 继续上一个session |
| `--session` | 指定session ID |
| `--agent` | 指定agent |

---

## 二、PM-Agent启动Agent流程

### 2.1 启动命令生成

```python
def generate_start_command(agent_id: str, project_path: str, prompt: str) -> str:
    """生成OpenCode启动命令"""
    return f'opencode "{project_path}" --prompt "{prompt}"'
```

### 2.2 启动执行

```python
import subprocess
import psutil
import os

class AgentManager:
    def __init__(self, pm_agent_url: str):
        self.pm_agent_url = pm_agent_url
    
    def start_agent(self, agent_id: str, project_id: int) -> bool:
        """启动Agent"""
        
        # 1. 获取Agent配置
        agent_config = self.get_agent_config(agent_id, project_id)
        
        # 2. 生成完整Prompt
        prompt = self.generate_prompt(agent_config)
        
        # 3. 启动OpenCode进程
        cmd = f'opencode "{agent_config["project_path"]}" --prompt "{prompt}"'
        
        process = subprocess.Popen(
            cmd,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=agent_config["project_path"]
        )
        
        # 4. 记录进程ID
        self.save_process_id(agent_id, project_id, process.pid)
        
        return True
    
    def stop_agent(self, agent_id: str, project_id: int) -> bool:
        """停止Agent"""
        
        # 1. 获取进程ID
        pid = self.get_process_id(agent_id, project_id)
        if not pid:
            return False
        
        # 2. 杀掉进程
        try:
            process = psutil.Process(pid)
            process.terminate()
            process.wait(timeout=5)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired:
            process.kill()
        
        # 3. 清理记录
        self.clear_process_id(agent_id, project_id)
        
        return True
    
    def restart_agent(self, agent_id: str, project_id: int) -> bool:
        """重启Agent"""
        self.stop_agent(agent_id, project_id)
        return self.start_agent(agent_id, project_id)
```

---

## 三、Agent状态管理

### 3.1 进程ID存储

```python
# PM-Agent数据库: agent_processes表
class AgentProcess(Base):
    __tablename__ = 'agent_processes'
    
    id = Column(Integer, primary_key=True)
    agent_id = Column(String(20), nullable=False)
    project_id = Column(Integer, nullable=False)
    process_id = Column(Integer)  # 进程ID
    status = Column(String(20), default='stopped')  # running/stopped
    started_at = Column(DateTime)
    last_heartbeat = Column(DateTime)
```

### 3.2 心跳检测

```python
def check_agent_heartbeat(agent_id: str, project_id: int) -> bool:
    """检查Agent是否存活"""
    pid = get_process_id(agent_id, project_id)
    if not pid:
        return False
    
    try:
        process = psutil.Process(pid)
        return process.is_running()
    except psutil.NoSuchProcess:
        return False
```

### 3.3 状态同步

```
┌─────────────────┐         ┌─────────────────┐
│   PM-Agent     │         │   Agent进程     │
│                 │         │                 │
│  agent_processes│◀───────▶│  心跳检测      │
│    表          │  定期检查 │                 │
└─────────────────┘         └─────────────────┘
```

---

## 四、Prompt追加方式

### 4.1 设计原则

**不替换OpenCode默认prompt，只追加Agent专属提示词到末尾**

### 4.2 追加模板

```
[OpenCode默认prompt]
---
[以下是Agent专属配置]

## 专属配置
- Agent ID: {agent_id}
- 开发者: {developer_name}
- 项目: {project_name}
- 技术栈: {tech_stack}

## 当前任务
{task_list}

开始工作。
```
```

---

## 五、PM-Agent界面操作

### 5.1 Agent列表

```
┌─────────────────────────────────────────────────────┐
│  项目: 金融法院卷宗系统                              │
│                                                     │
│  Agent管理:                                         │
│  ┌───────────────────────────────────────────────┐  │
│  │ Agent ID     │ 状态   │ 操作                   │  │
│  ├───────────────────────────────────────────────┤  │
│  │ agent1-001   │ 运行中 │ [停止] [重启] [日志]  │  │
│  │ agent1-002   │ 已停止 │ [启动]                │  │
│  │ agent3-001   │ 运行中 │ [停止] [重启] [日志]  │  │
│  └───────────────────────────────────────────────┘  │
│                                                     │
│  [+ 添加Agent]                                      │
└─────────────────────────────────────────────────────┘
```

### 5.2 API接口

```python
# 启动Agent
POST /api/agents/{agent_id}/start
{
    "project_id": 1
}

# 停止Agent
POST /api/agents/{agent_id}/stop
{
    "project_id": 1
}

# 重启Agent
POST /api/agents/{agent_id}/restart
{
    "project_id": 1
}

# 获取Agent状态
GET /api/agents/{agent_id}/status?project_id=1

# 获取Agent日志
GET /api/agents/{agent_id}/logs?project_id=1
```

---

## 六、实现优先级

| 功能 | 优先级 | 说明 |
|------|--------|------|
| 启动Agent | P0 | 核心功能 |
| 停止Agent | P0 | 核心功能 |
| 进程管理 | P0 | 进程ID存储 |
| 心跳检测 | P1 | 状态同步 |
| 日志查看 | P2 | 调试功能 |

---

## 七、技术依赖

| 依赖 | 用途 |
|------|------|
| `psutil` | 进程管理 |
| `subprocess` | 启动OpenCode |
| SQLite | 进程状态存储 |
