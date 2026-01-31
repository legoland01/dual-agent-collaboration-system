# 详细设计文档：oc-collab agent 守护进程

**版本**: v1  
**创建日期**: 2026-02-01  
**作者**: Agent 2 (开发)  
**关联需求版本**: v1.1

## 1. 概述

### 1.1 功能简介
本设计文档描述了"oc-collab agent 守护进程"功能的详细实现方案，包括：
- 后台模式（--daemon）
- 自动重启机制
- Git超时控制

### 1.2 模块位置
```
dual-agent-collaboration-system/
├── src/
│   ├── cli/
│   │   ├── agent.py          # Agent主类（已有）
│   │   └── main.py           # CLI入口（修改）
│   └── core/
│       ├── daemon.py         # 新增：后台模式实现
│       ├── supervisor.py     # 新增：进程监管（自动重启）
│       ├── git_monitor.py    # 修改：Git超时控制
│       └── state_manager.py  # 已有
├── scripts/
│   ├── agent_daemon.sh       # 可选：systemd 启动脚本
│   └── agent_watchdog.sh     # 可选：看门狗脚本
└── state/
    ├── agent_status.yaml     # 守护进程状态
    └── agent.pid             # PID文件
```

## 2. 架构设计

### 2.1 整体架构
```
┌─────────────────────────────────────────────────────────────────┐
│                      oc-collab agent 守护进程                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                                            │
│  │   CLI 入口      │  oc-collab agent [OPTIONS]                  │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────▼────────┐                                            │
│  │  参数解析       │  --daemon, --interval, --status             │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────▼────────┐                                            │
│  │  模式选择       │  前台模式 ←→ 后台模式                         │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────┴────────────────────────────────────────┐            │
│  │                  主循环                          │            │
│  │  ┌──────────────────────────────────────────┐   │            │
│  │  │           状态监控器                      │   │            │
│  │  │  ├─ 阶段状态监控                         │   │            │
│  │  │  ├─ Git状态监控 (含超时)                 │   │            │
│  │  │  └─ 签署状态监控                         │   │            │
│  │  └──────────────────────────────────────────┘   │            │
│  │                  │                                │            │
│  │  ┌───────────────▼───────────────┐               │            │
│  │  │         任务调度器             │               │            │
│  │  │  ├─ 阶段 → Agent 映射          │               │            │
│  │  │  └─ Agent 执行触发             │               │            │
│  │  └───────────────────────────────┘               │            │
│  │                  │                                │            │
│  │  ┌───────────────▼───────────────┐               │            │
│  │  │         阶段推进器             │               │            │
│  │  │  ├─ 条件检测                   │               │            │
│  │  │  └─ 状态更新                   │               │            │
│  │  └───────────────────────────────┘               │            │
│  └──────────────────────────────────────────────────┘            │
│           │                                                      │
│  ┌────────▼────────┐                                            │
│  │  进程监管       │  Supervisor (自动重启)                       │
│  └─────────────────┘                                            │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 类图
```
┌─────────────────────────────────────────────────────────────────┐
│                        类图                                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐                                            │
│  │   AgentDaemon   │  后台模式管理器                              │
│  ├─────────────────┤                                            │
│  │ - pid_file      │                                            │
│  │ - daemonize()   │                                            │
│  │ - write_pid()   │                                            │
│  │ - cleanup()     │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────▼────────┐                                            │
│  │  ProcessSupervisor│  进程监管器（自动重启）                     │
│  ├─────────────────┤                                            │
│  │ - restart_count │                                            │
│  │ - last_restart  │                                            │
│  │ - max_restarts  │                                            │
│  │ - backoff       │                                            │
│  │ - monitor()     │                                            │
│  │ - should_restart()                                           │
│  │ - get_backoff() │                                            │
│  └────────┬────────┘                                            │
│           │                                                      │
│  ┌────────┴──────────────────────────────────────┐              │
│  │                    Agent                      │              │
│  │  (现有类，增加以下方法)                         │              │
│  ├──────────────────────────────────────────────┤              │
│  │ + set_git_timeout(timeout_config: Dict)      │              │
│  │ + get_daemon_status() -> Dict                │              │
│  └──────────────────────────────────────────────┘              │
└─────────────────────────────────────────────────────────────────┘
```

## 3. 模块设计

### 3.1 AgentDaemon - 后台模式

**职责**: 实现守护进程后台运行

**属性**:
| 属性 | 类型 | 说明 |
|------|------|------|
| pid_file | Path | PID文件路径 |
| log_file | Path | 日志文件路径 |
| work_dir | Path | 工作目录 |

**方法**:

```python
class AgentDaemon:
    """守护进程后台运行管理器。"""
    
    DEFAULT_PID_FILE = "state/agent.pid"
    DEFAULT_LOG_FILE = "logs/agent_daemon.log"
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.pid_file = self.project_path / self.DEFAULT_PID_FILE
        self.log_file = self.project_path / self.DEFAULT_LOG_FILE
        self.work_dir = self.project_path
    
    def daemonize(self, main_func: Callable, *args, **kwargs) -> int:
        """
        将进程转换为守护进程
        
        Returns:
            int: 父进程返回子进程PID，子进程不返回
        """
        # 1. 检查是否已运行
        if self.is_running():
            pid = self.get_running_pid()
            raise ProcessExistsError(f"Agent 已在运行 (PID: {pid})")
        
        # 2. 创建日志目录
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 3. fork 子进程
        try:
            pid = os.fork()
            if pid > 0:
                # 父进程返回子进程 PID
                return pid
        except OSError as e:
            raise DaemonizeError(f"Fork 失败: {e}")
        
        # 子进程继续执行
        # 4. 创建新会话
        os.setsid()
        
        # 5. 改变工作目录
        os.chdir(self.work_dir)
        
        # 6. 重定向标准输入/输出/错误
        sys.stdout.flush()
        sys.stderr.flush()
        
        with open('/dev/null', 'r') as devnull:
            os.dup2(devnull.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+') as devnull:
            os.dup2(devnull.fileno(), sys.stdout.fileno())
            os.dup2(devnull.fileno(), sys.stderr.fileno())
        
        # 7. 写入 PID 文件
        self.write_pid()
        
        # 8. 设置信号处理
        signal.signal(signal.SIGTERM, self._handle_terminate)
        signal.signal(signal.SIGINT, self._handle_terminate)
        
        # 9. 执行主函数
        try:
            main_func(*args, **kwargs)
        except Exception as e:
            self._log(f"守护进程异常: {e}")
            raise
        finally:
            self.cleanup()
    
    def is_running(self) -> bool:
        """检查是否正在运行。"""
        if not self.pid_file.exists():
            return False
        try:
            pid = int(self.pid_file.read_text().strip())
            os.kill(pid, 0)  # 检查进程是否存在
            return True
        except (ProcessLookupError, ValueError, PermissionError):
            return False
    
    def get_running_pid(self) -> Optional[int]:
        """获取运行中的 PID。"""
        if self.pid_file.exists():
            try:
                return int(self.pid_file.read_text().strip())
            except (ValueError, IOError):
                return None
        return None
    
    def write_pid(self) -> None:
        """写入 PID 文件。"""
        self.pid_file.parent.mkdir(parents=True, exist_ok=True)
        self.pid_file.write_text(str(os.getpid()))
    
    def cleanup(self) -> None:
        """清理资源。"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def stop(self) -> bool:
        """停止守护进程。"""
        pid = self.get_running_pid()
        if pid is None:
            return False
        try:
            os.kill(pid, signal.SIGTERM)
            return True
        except ProcessLookupError:
            return True
        except PermissionError:
            return False
    
    def _handle_terminate(self, signum, frame) -> None:
        """处理终止信号。"""
        self._log(f"收到信号 {signum}，正在停止...")
        self.cleanup()
        sys.exit(0)
    
    def _log(self, message: str) -> None:
        """写入日志。"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] {message}\n"
        with open(self.log_file, 'a') as f:
            f.write(log_line)
```

### 3.2 ProcessSupervisor - 进程监管器

**职责**: 监控子进程状态，异常时自动重启

**属性**:
| 属性 | 类型 | 说明 |
|------|------|------|
| max_restarts | int | 最大重启次数（默认5） |
| time_window | int | 时间窗口（默认3600秒=1小时） |
| restart_count | int | 当前时间窗口内重启次数 |
| last_restart | datetime | 最后重启时间 |
| backoff_factor | int | 退避因子（默认2） |

**方法**:

```python
class ProcessSupervisor:
    """进程监管器（自动重启机制）。"""
    
    DEFAULT_MAX_RESTARTS = 5
    DEFAULT_TIME_WINDOW = 3600  # 1小时
    DEFAULT_BACKOFF_FACTOR = 2
    
    def __init__(self, project_path: str, 
                 max_restarts: int = None,
                 time_window: int = None,
                 backoff_factor: int = None):
        self.project_path = Path(project_path)
        self.max_restarts = max_restarts or self.DEFAULT_MAX_RESTARTS
        self.time_window = time_window or self.DEFAULT_TIME_WINDOW
        self.backoff_factor = backoff_factor or self.DEFAULT_BACKOFF_FACTOR
        
        self.restart_count = 0
        self.last_restart = None
        self.process = None
        self.is_running = False
    
    def start(self, main_func: Callable, *args, **kwargs) -> bool:
        """
        启动监管进程
        
        Returns:
            bool: 是否成功启动
        """
        self.is_running = True
        backoff = 1
        
        while self.is_running and self.should_start():
            try:
                self._log(f"启动进程 (重试次数: {self.restart_count}, 退避: {backoff}s)")
                
                # 启动进程
                self.process = subprocess.Popen(
                    [sys.executable, '-c', self._create_wrapper(main_func, args, kwargs)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    cwd=str(self.project_path)
                )
                
                # 等待进程完成
                return_code = self.process.wait()
                
                if return_code == 0:
                    self._log("进程正常退出")
                    break
                else:
                    self._log(f"进程异常退出 (返回码: {return_code})")
                    
            except Exception as e:
                self._log(f"进程启动失败: {e}")
            
            # 检查是否应该重启
            if self.should_start():
                self._record_restart()
                time.sleep(backoff)
                backoff = min(backoff * self.backoff_factor, 60)  # 最大退避60秒
                self.restart_count += 1
            else:
                self._log("超过最大重启次数，停止监管")
                break
        
        return not self.is_running
    
    def stop(self) -> None:
        """停止监管。"""
        self.is_running = False
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
    
    def should_start(self) -> bool:
        """检查是否应该启动进程。"""
        # 检查是否超过时间窗口
        if self.last_restart:
            elapsed = (datetime.now() - self.last_restart).total_seconds()
            if elapsed > self.time_window:
                self.restart_count = 0  # 重置计数
        
        return self.restart_count < self.max_restarts
    
    def _record_restart(self) -> None:
        """记录重启。"""
        self.last_restart = datetime.now()
    
    def _create_wrapper(self, main_func: Callable, args: tuple, kwargs: dict) -> str:
        """创建进程包装脚本。"""
        import pickle
        return f"""
import sys
import pickle
sys.path.insert(0, '{self.project_path}')

func, args, kwargs = pickle.loads({pickle.dumps((main_func, args, kwargs))})
func(*args, **kwargs)
"""
    
    def _log(self, message: str) -> None:
        """记录日志。"""
        print(f"[Supervisor] {message}")
```

### 3.3 Git 超时控制

**修改位置**: `src/core/git.py`

**新增功能**:
```python
class GitHelper:
    """Git 操作助手（支持超时控制）。"""
    
    DEFAULT_TIMEOUTS = {
        'status': 10,
        'add': 5,
        'commit': 10,
        'push': 60,
        'pull': 30,
        'log': 10,
        'diff': 10
    }
    
    def __init__(self, project_path: str, timeouts: Dict[str, int] = None):
        self.project_path = Path(project_path)
        self.timeouts = {**self.DEFAULT_TIMEOUTS, **(timeouts or {})}
    
    def _run_git(self, args: List[str], timeout_key: str) -> subprocess.CompletedProcess:
        """运行 Git 命令（带超时）。"""
        timeout = self.timeouts.get(timeout_key, 10)
        try:
            return subprocess.run(
                ['git'] + args,
                cwd=self.project_path,
                timeout=timeout,
                capture_output=True,
                text=True
            )
        except subprocess.TimeoutExpired:
            raise GitTimeoutError(f"Git 命令超时 ({timeout_key}: {timeout}s)")
    
    def status(self) -> Dict[str, Any]:
        """获取 Git 状态（10秒超时）。"""
        result = self._run_git(['status', '--porcelain'], 'status')
        return self._parse_status(result.stdout)
    
    def add(self, files: List[str] = None) -> bool:
        """添加文件（5秒超时）。"""
        args = ['add']
        if files:
            args.extend(files)
        else:
            args.append('.')
        result = self._run_git(args, 'add')
        return result.returncode == 0
    
    def commit(self, message: str) -> bool:
        """提交（10秒超时）。"""
        result = self._run_git(['commit', '-m', message], 'commit')
        return result.returncode == 0
    
    def push(self, remote: str = 'origin', branch: str = None) -> bool:
        """推送（60秒超时）。"""
        args = ['push']
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        result = self._run_git(args, 'push')
        return result.returncode == 0
    
    def pull(self, remote: str = 'origin', branch: str = None) -> bool:
        """拉取（30秒超时）。"""
        args = ['pull']
        if remote:
            args.append(remote)
        if branch:
            args.append(branch)
        result = self._run_git(args, 'pull')
        return result.returncode == 0
```

### 3.4 CLI 命令修改

**修改位置**: `src/cli/main.py`

```python
import click
from .agent import Agent, AgentConfig, AgentMode
from ..core.daemon import AgentDaemon
from ..core.supervisor import ProcessSupervisor

@click.group()
def agent():
    """Agent 守护进程命令组。"""
    pass

@agent.command()
@click.option('--interval', '-i', default=30, help='状态检查间隔（秒）')
@click.option('--daemon', '-d', is_flag=True, help='后台模式运行')
@click.option('--supervise', '-s', is_flag=True, help='监管模式（自动重启）')
def start(interval: int, daemon: bool, supervise: bool):
    """启动 Agent 守护进程。"""
    from ..core.state_manager import StateManager
    
    project_path = '.'
    state_manager = StateManager(project_path)
    
    def main_loop():
        agent = Agent(AgentConfig(
            agent_id="agent_daemon",
            agent_type="Daemon",
            polling_interval=interval
        ))
        agent.initialize(project_path, state_manager)
        agent.start()
        
        # 保持运行
        while True:
            time.sleep(1)
    
    if supervise:
        # 监管模式
        supervisor = ProcessSupervisor(project_path)
        supervisor.start(main_loop)
    elif daemon:
        # 后台模式
        daemonizer = AgentDaemon(project_path)
        pid = daemonizer.daemonize(main_loop)
        click.echo(f"守护进程已启动 (PID: {pid})")
    else:
        # 前台模式
        click.echo("启动 Agent 守护进程（前台模式）...")
        main_loop()

@agent.command()
def status():
    """查看 Agent 守护进程状态。"""
    import os
    pid_file = Path("state/agent.pid")
    
    if pid_file.exists():
        pid = int(pid_file.read_text().strip())
        try:
            os.kill(pid, 0)
            click.echo(f"Agent 守护进程运行中 (PID: {pid})")
        except ProcessLookupError:
            click.echo("Agent 守护进程未运行（PID文件存在但进程不存在）")
    else:
        click.echo("Agent 守护进程未运行")

@agent.command()
def stop():
    """停止 Agent 守护进程。"""
    daemonizer = AgentDaemon('.')
    if daemonizer.stop():
        click.echo("Agent 守护进程已停止")
    else:
        click.echo("Agent 守护进程停止失败或未运行")
```

## 4. 数据结构

### 4.1 PID 文件
**路径**: `state/agent.pid`

**内容**:
```
12345
```

### 4.2 守护进程状态文件
**路径**: `state/agent_status.yaml`

**结构**:
```yaml
status: running
last_check: "2026-02-01T12:00:00"
agents_run: 10
errors: 0
start_time: "2026-02-01T12:00:00"
uptime_seconds: 3600
```

### 4.3 日志文件
**路径**: `logs/agent_daemon.log`

**格式**:
```
[2026-02-01T12:00:00.000000] 守护进程已启动 (PID: 12345)
[2026-02-01T12:00:30.000000] 检测到阶段变更: testing -> deployment
[2026-02-01T12:01:00.000000] Agent 1 执行完成
```

## 5. 异常处理

### 5.1 异常场景

| 场景 | 处理方式 |
|------|----------|
| PID文件已存在 | 拒绝启动，提示已运行 |
| fork失败 | 抛出 DaemonizeError |
| 超过最大重启次数 | 停止尝试，抛出异常 |
| Git操作超时 | 抛出 GitTimeoutError |
| 进程被信号终止 | 清理资源，正常退出 |

### 5.2 自定义异常

```python
class AgentDaemonError(Exception):
    """守护进程异常基类。"""
    pass

class ProcessExistsError(AgentDaemonError):
    """进程已存在异常。"""
    pass

class DaemonizeError(AgentDaemonError):
    """守护进程化异常。"""
    pass

class GitTimeoutError(AgentDaemonError):
    """Git 超时异常。"""
    pass
```

## 6. 测试用例

### 6.1 单元测试

| 用例编号 | 用例描述 | 预期结果 |
|----------|----------|----------|
| TC-DAEMON-001 | 后台模式启动 | 进程 fork 成功，PID 文件写入 |
| TC-DAEMON-002 | 重复启动 | 抛出 ProcessExistsError |
| TC-DAEMON-003 | 停止守护进程 | 发送 SIGTERM，清理 PID 文件 |
| TC-DAEMON-004 | SIGTERM 信号处理 | 优雅退出，清理资源 |
| TC-SUPER-001 | 进程正常退出 | 监管器正常退出 |
| TC-SUPER-002 | 进程异常退出 | 自动重启 |
| TC-SUPER-003 | 超过最大重启次数 | 停止尝试 |
| TC-GIT-001 | Git 操作未超时 | 正常完成 |
| TC-GIT-002 | Git 操作超时 | 抛出 GitTimeoutError |

### 6.2 集成测试

| 用例编号 | 用例描述 | 预期结果 |
|----------|----------|----------|
| TC-INT-001 | 后台模式 + 状态监控 | 守护进程正常运行，状态更新 |
| TC-INT-002 | 监管模式 + 阶段推进 | 异常退出后自动重启 |
| TC-INT-003 | Git 超时 + 重试 | 超时后重试或报错 |

## 7. 安全性考虑

### 7.1 进程隔离
- 守护进程使用新会话（setsid）
- 标准输入/输出/错误重定向到 /dev/null

### 7.2 文件权限
- PID 文件权限设置为 0644
- 避免权限泄露

### 7.3 信号处理
- 正确处理 SIGTERM 和 SIGINT
- 优雅关闭，避免数据丢失

## 8. 性能考虑

### 8.1 资源消耗
| 操作 | 资源消耗 |
|------|----------|
| 后台模式 fork | 一次性内存复制（写时复制） |
| 状态检查 | O(1) - 读取状态文件 |
| Git 超时控制 | 防止长时间阻塞 |

### 8.2 并发处理
- 使用信号量避免竞态条件
- PID 文件检查和写入原子化

## 9. 兼容性

### 9.1 平台支持
| 平台 | 支持情况 |
|------|----------|
| Linux | ✅ 完全支持 |
| macOS | ✅ 完全支持 |
| Windows | ⚠️ 部分支持（daemonize 不支持） |

### 9.2 向后兼容
- 现有 CLI 命令保持不变
- 新增 `--daemon` 和 `--supervise` 参数
- 不修改现有状态文件结构

## 10. 部署说明

### 10.1 部署步骤
1. 部署更新的 `src/cli/main.py`
2. 部署新增的 `src/core/daemon.py`
3. 部署新增的 `src/core/supervisor.py`
4. 创建日志目录 `logs/`

### 10.2 使用方式

```bash
# 前台运行（调试用）
oc-collab agent start

# 后台运行
oc-collab agent start --daemon

# 监管模式（自动重启）
oc-collab agent start --supervise

# 查看状态
oc-collab agent status

# 停止
oc-collab agent stop
```

### 10.3 systemd 集成（可选）

创建 `/etc/systemd/system/oc-collab-agent.service`:
```ini
[Unit]
Description=oc-collab Agent Daemon
After=network.target

[Service]
Type=simple
User=occollab
WorkingDirectory=/path/to/project
ExecStart=/usr/bin/oc-collab agent start --daemon
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 11. 实现检查清单

- [ ] 实现 `AgentDaemon` 类
- [ ] 实现 `ProcessSupervisor` 类
- [ ] 修改 `GitHelper` 添加超时控制
- [ ] 修改 CLI 添加 `--daemon` 和 `--supervise` 参数
- [ ] 编写单元测试
- [ ] 编写集成测试
- [ ] 更新文档
