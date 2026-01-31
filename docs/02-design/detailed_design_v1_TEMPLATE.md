# 双Agent协作框架 - 详细设计

## 版本信息
- **版本**: v1
- **关联需求版本**: v2
- **创建日期**: [日期]
- **作者**: Agent 2 (开发)

## 1. 系统架构

### 1.1 整体架构
[参考系统设计文档，补充实现细节]

### 1.2 模块划分
[详细描述各模块的职责和接口]

## 2. 核心模块详细设计

### 2.1 CLI 命令模块 (cli/main.py)

**命令定义**：
| 命令 | 函数 | 描述 |
|-----|------|------|
| `init` | `init()` | 初始化协作项目 |
| `status` | `status()` | 查看当前状态 |
| `switch` | `switch()` | 切换 Agent 角色 |
| `review` | `review()` | 管理评审 |
| `signoff` | `signoff()` | 签署确认 |
| `history` | `history()` | 查看历史 |
| `sync` | `sync()` | 同步变更 |

**参数选项**：
```python
# init 命令
@main.command("init")
@click.argument("project_name")
@click.option("--type", "-t", type=click.Choice(["python", "typescript", "mixed", "auto"]))
@click.option("--force/--no-force", "-f")
@click.option("--no-git")

# switch 命令
@main.command("switch")
@click.argument("agent_id", type=click.IntRange(1, 2))

# signoff 命令
@main.command("signoff")
@click.argument("stage", type=click.Choice(["requirements", "design", "test"]))
@click.option("--comment", "-m")
```

### 2.2 状态管理器 (core/state_manager.py)

**类定义**：
```python
class StateManager:
    def __init__(self, project_path: str):
        self.state_file = Path(project_path) / "state" / "project_state.yaml"
    
    def load_state(self) -> dict:
        """加载状态文件"""
    
    def save_state(self, state: dict):
        """保存状态文件"""
    
    def update_phase(self, phase: str):
        """更新当前阶段"""
    
    def update_signoff(self, stage: str, agent: str, signed: bool):
        """更新签署状态"""
    
    def get_current_phase(self) -> str:
        """获取当前阶段"""
    
    def get_signoff_status(self, stage: str) -> dict:
        """获取签署状态"""
```

### 2.3 项目检测器 (core/detector.py)

**检测规则**：
```python
def detect_project_type(project_path: str) -> str:
    # Python: pyproject.toml, setup.py, requirements.txt
    # TypeScript: package.json, tsconfig.json
    # Mixed: 多种语言特征
    # Default: auto-detect or ask user
```

### 2.4 Git 集成模块 (core/git.py)

**Git 操作封装**：
```python
class GitHelper:
    def __init__(self, project_path: str):
        self.repo = Repo(project_path)
    
    def pull(self):
        """拉取远程变更"""
    
    def push(self, message: str):
        """提交并推送"""
    
    def create_branch(self, branch_name: str):
        """创建分支"""
    
    def create_tag(self, tag_name: str, message: str):
        """创建标签"""
```

## 3. 数据结构

### 3.1 状态文件
```python
# state/project_state.yaml
state = {
    "version": "1.0.0",
    "project": {
        "name": str,
        "type": str,  # PYTHON/TYPESCRIPT/MIXED
        "created_at": str,
        "updated_at": str
    },
    "phase": str,
    "agents": {
        "agent1": {"role": str, "current": bool},
        "agent2": {"role": str, "current": bool}
    },
    "requirements": {
        "version": str,
        "status": str,
        "pm_signoff": bool,
        "dev_signoff": bool,
        "review_cycles": int
    },
    "design": {...},
    "test": {...},
    "development": {...},
    "deployment": {...}
}
```

### 3.2 错误码定义
```python
ERROR_CODES = {
    1001: "参数错误: 无效的命令参数",
    1002: "参数错误: 缺少必需参数",
    2001: "文件错误: 文件不存在",
    2002: "文件错误: 文件解析失败",
    2003: "文件错误: 文件写入失败",
    3001: "Git 错误: Git 操作失败",
    3002: "Git 错误: 远程仓库连接失败",
    3003: "Git 错误: 合并冲突",
    4001: "状态错误: 无效的阶段转换",
    4002: "状态错误: 签署条件不满足",
    5001: "权限错误: 无操作权限"
}
```

## 4. 接口设计

### 4.1 状态转换接口

```python
# 有效阶段转换
VALID_PHASE_TRANSITIONS = {
    "project_init": ["requirements_draft"],
    "requirements_draft": ["requirements_review"],
    "requirements_review": ["requirements_draft", "requirements_approved"],
    "requirements_approved": ["design_draft"],
    "design_draft": ["design_review"],
    "design_review": ["design_draft", "design_approved"],
    "design_approved": ["development"],
    "development": ["testing"],
    "testing": ["deployment", "development"],
    "deployment": ["completed"]
}
```

### 4.2 签署条件验证

```python
def can_sign(stage: str, agent: str, state: dict) -> tuple[bool, str]:
    """检查是否可以签署"""
    if stage == "requirements":
        if agent == "agent1" and state["requirements"]["pm_signoff"]:
            return False, "产品经理已签署"
        if agent == "agent2" and state["requirements"]["dev_signoff"]:
            return False, "开发已签署"
    # ... 其他阶段类似
    return True, ""
```

## 5. 文件结构

```
src/
├── cli/
│   ├── __init__.py
│   ├── main.py          # Click 命令入口
│   ├── init.py          # init 命令
│   ├── status.py        # status 命令
│   ├── switch.py        # switch 命令
│   ├── review.py        # review 命令
│   ├── signoff.py       # signoff 命令
│   ├── history.py       # history 命令
│   └── sync.py          # sync 命令
│
├── core/
│   ├── __init__.py
│   ├── state_manager.py # 状态管理
│   ├── detector.py      # 项目检测
│   ├── git.py          # Git 操作
│   ├── workflow.py     # 工作流引擎
│   └── signoff.py      # 签署引擎
│
├── utils/
│   ├── __init__.py
│   ├── yaml.py         # YAML 读写
│   ├── file.py         # 文件操作
│   └── date.py         # 日期工具
│
└── templates/
    ├── __init__.py
    └── renderer.py      # 模板渲染
```

## 6. 依赖配置

```toml
# pyproject.toml
[project.dependencies]
click = ">=8.0"
pyyaml = ">=6.0"
jinja2 = ">=3.0"
gitpython = ">=3.0"
rich = ">=12.0"
inquirer = ">=2.0"
```

## 7. 测试设计

### 7.1 单元测试
- `test_state_manager.py`: 状态读写测试
- `test_detector.py`: 项目检测测试
- `test_git.py`: Git 操作测试
- `test_workflow.py`: 状态转换测试

### 7.2 集成测试
- `test_cli_init.py`: CLI init 命令测试
- `test_cli_signoff.py`: CLI signoff 命令测试
- `test_full_workflow.py`: 完整流程测试

## 8. 实现计划

| 模块 | 优先级 | 预估工时 |
|-----|-------|---------|
| CLI 框架 | P0 | 1 天 |
| 状态管理器 | P0 | 0.5 天 |
| Git 集成 | P0 | 1 天 |
| 项目检测器 | P1 | 0.5 天 |
| 工作流引擎 | P1 | 1 天 |
| 签署引擎 | P1 | 0.5 天 |
| 模板引擎 | P2 | 1 天 |
| 测试 | P0 | 2 天 |

## 9. 待确定事项

1. [ ] 是否需要支持多语言模板？
2. [ ] 审计日志的存储格式？
3. [ ] 是否需要 Webhook 通知？
