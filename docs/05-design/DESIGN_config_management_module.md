# 配置管理模块设计方案

**日期**: 2026-02-17  
**状态**: 初稿  
**类型**: 架构设计

---

## 一、问题分析

### 1.1 当前问题

**现象**: 
- Agent2运行时使用旧版本的检查机制
- 新功能上线后，旧检查机制阻止新功能执行
- todowrite指令因版本不匹配发送失败

**根本原因**:
- 缺少统一的配置/版本管理机制
- 硬编码版本号分散在代码各处
- 运行时无法感知配置变更

### 1.2 问题示例

```python
# 问题1: 硬编码版本号
# v2.2.9: StateNotifier集成 - 发送Webhook通知

# 问题2: 缺少版本检查
def todowrite():
    # 新功能上线，但旧检查逻辑可能阻止执行
    if old_check():
        block()
    new_feature()  # 可能永远不会执行

# 问题3: 配置不同步
# Agent1更新了Skill
# Agent2运行时加载的是旧版本
```

---

## 二、设计目标

### 2.1 核心目标

| 目标 | 说明 |
|------|------|
| **版本感知** | 每个模块知道自己的版本 |
| **版本检查** | 运行时检查是否需要更新 |
| **强制同步** | 确保所有Agent使用相同版本配置 |
| **热更新** | 无需重启即可加载新配置 |
| **跨项目同步** | 全局配置，所有项目共享 |
| **Skill版本管理** | Skill变化自动同步到所有Agent |

### 2.2 非目标

- 不包含业务逻辑变更
- 不替代PyPI版本管理
- 不处理代码层面的依赖

---

## 三、架构设计

### 3.1 模块结构

```
~/.config/opencode/           # 全局配置目录
├── config_registry.yaml     # 全局版本注册表
├── global_skills.yaml       # 全局Skill版本
└── projects.yaml           # 项目列表

项目目录/
├── state/
│   ├── config_registry.yaml     # 项目本地注册表
│   └── local_overrides.yaml    # 本地覆盖配置
```

### 3.2 核心数据结构

**全局版本注册表** (`~/.config/opencode/config_registry.yaml`):

```yaml
version: "1.0"
last_updated: "2026-02-17T12:00:00Z"

# 核心模块版本（全局）
modules:
  skill_enforcer:
    version: "2.3.1"
    min_version: "2.2.6"
    last_updated: "2026-02-17T10:00:00Z"
    source: "pyproject.toml"
    
  compliance_checker:
    version: "2.3.1"
    min_version: "2.3.0"
    last_updated: "2026-02-17T11:00:00Z"
    source: "pyproject.toml"

# Skill版本（全局同步）
skills:
  oc_collab_requirements_guide:
    version: "2.3.1"
    hash: "abc123..."
    last_updated: "2026-02-17T10:00:00Z"
    projects: ["project-A", "project-B"]  # 使用此Skill的项目
    
  oc_collab_deployment_guide:
    version: "2.3.0"
    hash: "def456..."
    last_updated: "2026-02-16T10:00:00Z"
    projects: ["project-A"]

# 项目列表
projects:
  project-A:
    path: "/path/to/project-A"
    last_sync: "2026-02-17T12:00:00Z"
    status: "current"
  project-B:
    path: "/path/to/project-B"
    last_sync: "2026-02-17T11:00:00Z"
    status: "outdated"
```

**项目本地注册表** (`项目/state/config_registry.yaml`):

```yaml
version: "1.0"
last_updated: "2026-02-17T12:00:00Z"

# 继承全局配置
inherited_from: "~/.config/opencode/config_registry.yaml"

# 本地覆盖（可选）
overrides:
  custom_check: true

# Agent运行时版本
agents:
  agent1:
    current_version: "2.3.1"
    last_check: "2026-02-17T12:00:00Z"
    status: "current"
  agent2:
    current_version: "2.2.9"  # 旧版本！
    last_check: "2026-02-17T11:00:00Z"
    status: "outdated"
```

### 3.3 核心类设计

```python
class ConfigRegistry:
    """版本注册表管理器"""
    
    def register_module(self, module_name: str, version: str, metadata: dict):
        """注册模块版本"""
        
    def get_module_version(self, module_name: str) -> Optional[str]:
        """获取模块版本"""
        
    def check_version_compatibility(self, module_name: str) -> VersionStatus:
        """检查版本兼容性"""
        
    def sync_with_remote(self) -> SyncResult:
        """同步远程配置"""
        

class VersionChecker:
    """版本检查器"""
    
    def check_all_modules(self) -> List[VersionIssue]:
        """检查所有模块版本"""
        
    def check_module(self, module_name: str) -> VersionIssue:
        """检查单个模块"""
        
    def require_min_version(self, module_name: str, min_version: str):
        """要求最低版本，低于则阻止运行"""
        

class ConfigWatcher:
    """配置变更监听器"""
    
    def watch(self, callback: Callable):
        """监听配置变更"""
        
    def start_watching(self):
        """启动监听"""
        
    def stop_watching(self):
        """停止监听"""
```

---

## 四、功能设计

### 4.1 版本注册

**自动注册**:
- 启动时自动从pyproject.toml读取版本
- 首次运行时生成版本注册表
- Skill加载时自动注册版本

**全局注册** (跨项目):
```bash
# 注册到全局配置
oc-collab config register --global --module skill_enforcer --version 2.3.1

# 查看全局配置
oc-collab config status --global
```

### 4.2 Skill版本管理

**问题**: Skill更新后，其他Agent未同步

**解决**:
```python
class SkillVersionManager:
    """Skill版本管理器"""
    
    def load_skill(self, skill_name: str):
        # 检查全局配置中的Skill版本
        global_version = self.get_global_skill_version(skill_name)
        local_version = self.get_local_skill_version(skill_name)
        
        if global_version != local_version:
            # 提示同步
            print(f"Skill '{skill_name}' 有新版本: {global_version}")
            print("执行 'oc-collab config sync-skills' 同步")
            
        # 加载Skill
        ...
    
    def sync_all_skills(self):
        """同步所有项目的Skills"""
        # 从全局配置获取最新Skill版本
        # 更新到每个项目
        ...
```

**数据流**:
```
Agent1 更新Skill
    ↓
更新全局 config_registry.yaml (skills字段)
    ↓
Git push
    ↓
其他项目 pull
    ↓
Agent2 启动时检测到Skill版本变化
    ↓
提示同步或自动更新
```

### 4.3 跨项目同步

**场景**: 
- 项目A更新了配置
- 项目B需要同步

**解决**:
```python
class ProjectSyncManager:
    """项目同步管理器"""
    
    def sync_from_global(self):
        """从全局配置同步"""
        global_config = load("~/.config/opencode/config_registry.yaml")
        local_config = load("state/config_registry.yaml")
        
        # 合并配置
        merged = merge(local_config, global_config)
        save("state/config_registry.yaml")
    
    def sync_to_projects(self, target_projects: List[str]):
        """同步到其他项目"""
        for project in target_projects:
            # 复制全局配置到项目
            copy_global_to_project(project)
```

### 4.4 版本检查

**检查时机**:
| 时机 | 检查内容 |
|------|----------|
| Agent启动 | 检查所有依赖模块版本 + Skill版本 |
| CLI命令执行前 | 检查相关模块版本 |
| Skill加载时 | 检查是否需要同步 |
| 定时检查 | 每5分钟检查一次 |

**检查结果**:
```python
class VersionIssue:
    module_name: str
    current_version: str
    required_version: str
    severity: "error" | "warning" | "info"
    message: str
    fix_command: str  # 修复命令
    is_skill: bool    # 是否是Skill问题
    is_cross_project: bool  # 是否需要跨项目同步
```

### 4.5 强制同步

**同步策略**:

| 策略 | 触发条件 | 动作 |
|------|----------|------|
| **BLOCK** | 当前版本 < 最低版本 | 阻止运行，要求升级 |
| **WARN** | 当前版本 < 推荐版本 | 警告，可继续 |
| **SKILL_OUTDATED** | Skill版本过期 | 提示同步Skill |
| **PROJECT_OUTDATED** | 项目配置过期 | 提示同步项目 |

**示例**:
```python
# 当前版本 2.2.9，最低要求 2.3.0
# → 阻止运行，提示执行升级命令

# Skill版本过期
# → 提示执行: oc-collab config sync-skills

# 项目配置过期
# → 提示执行: oc-collab config sync --project project-B
```

### 4.3 强制同步

**同步策略**:

| 策略 | 触发条件 | 动作 |
|------|----------|------|
| **BLOCK** | 当前版本 < 最低版本 | 阻止运行，要求升级 |
| **WARN** | 当前版本 < 推荐版本 | 警告，可继续 |
| **INFO** | 有新版本可用 | 提示有新版本 |

**示例**:
```python
# 当前版本 2.2.9，最低要求 2.3.0
# → 阻止运行，提示执行升级命令

# 当前版本 2.3.0，推荐版本 2.3.1
# → 警告但允许运行
```

### 4.4 热更新

**监听机制**:
- 使用文件系统监听 (watchdog)
- 检测到配置变更时自动重新加载
- 通过EventEmitter通知订阅者

**更新传播**:
```
Agent1 更新Skill
    ↓
写入 config_registry.yaml
    ↓
ConfigWatcher 检测到变更
    ↓
EventEmitter 广播变更事件
    ↓
Agent2 收到事件，重新加载配置
```

---

## 五、CLI命令

### 5.1 命令列表

| 命令 | 说明 |
|------|------|
| `oc-collab config status` | 查看配置状态（默认本地） |
| `oc-collab config status --global` | 查看全局配置状态 |
| `oc-collab config status --all-projects` | 查看所有项目配置 |
| `oc-collab config check` | 检查版本 |
| `oc-collab config sync` | 同步本地配置 |
| `oc-collab config sync --global` | 同步全局配置 |
| `oc-collab config sync --project <name>` | 同步指定项目 |
| `oc-collab config sync-skills` | 同步所有Skills |
| `oc-collab config register` | 注册模块版本 |
| `oc-collab config watch` | 启动配置监听 |
| `oc-collab config project add <path>` | 添加项目到管理 |
| `oc-collab config project remove <name>` | 移除项目 |

### 5.2 命令示例

```bash
# 查看全局配置状态
$ oc-collab config status --global
┌─────────────────┬───────────┬───────────┬──────────┐
│ Skill           │ 全局版本  │ 本地版本  │ 状态     │
├─────────────────┼───────────┼───────────┼──────────┤
│ requirements    │ 2.3.1     │ 2.3.0     │ ⚠️  建议升级│
│ deployment      │ 2.3.0     │ 2.3.0     │ ✅ 同步   │
└─────────────────┴───────────┴───────────┴──────────┘

# 查看所有项目
$ oc-collab config status --all-projects
┌────────────┬────────────┬───────────┬──────────┐
│ 项目        │ 路径       │ 状态      │ 最后同步  │
├────────────┼────────────┼───────────┼──────────┤
│ project-A  │ /path/A   │ ✅ 当前   │ 12:00   │
│ project-B  │ /path/B   │ ⚠️ 过期   │ 11:00   │
└────────────┴────────────┴───────────┴──────────┘

# 同步Skills
$ oc-collab config sync-skills
[OK] Skills已同步:
- oc_collab_requirements_guide: 2.3.0 → 2.3.1
- oc_collab_deployment_guide: 已最新

# 检查版本问题
$ oc-collab config check
[ERROR] agent2 使用旧版本 2.2.9
[WARNING] Skill 'requirements_guide' 版本过期
[ERROR] project-B 配置过期，请执行: oc-collab config sync --project project-B
```

---

## 六、与现有模块集成

### 6.1 SkillEnforcer集成

```python
class SkillEnforcer:
    def __init__(self):
        self.config = ConfigRegistry()
        
    def check(self, action: str):
        # 版本检查
        version_status = self.config.check_version_compatibility("skill_enforcer")
        if version_status.severity == "error":
            raise VersionError(f"请先升级到最新版本: {version_status.fix_command}")
        
        # 原有逻辑
        ...
```

### 6.2 todowrite集成

```python
def todowrite():
    # 检查版本
    checker = VersionChecker()
    issues = checker.check_all_modules()
    
    if issues.has_errors():
        # 阻止执行，提供修复命令
        print(f"版本检查失败: {issues.summary()}")
        print(f"请执行: {issues[0].fix_command}")
        return
        
    # 原有逻辑
    ...
```

---

## 七、数据流

### 7.1 启动时检查

```
Agent启动
    ↓
加载 config_registry.yaml
    ↓
检查每个模块版本
    ↓
┌─ 有问题 ─→ 阻止启动，提供修复命令
└─ 正常 ─→ 继续启动
```

### 7.2 命令执行前检查

```
用户执行 oc-collab todowrite
    ↓
检查相关模块版本 (skill_enforcer, compliance)
    ↓
┌─ 有问题 ─→ 阻止执行，提示修复
└─ 正常 ─→ 执行命令
```

### 7.3 配置变更传播

```
Agent1 更新Skill/配置
    ↓
更新 config_registry.yaml
    ↓
Git push
    ↓
Agent2 Git pull
    ↓
ConfigWatcher 检测到变更
    ↓
重新加载配置
```

---

## 八、文件结构

```
state/
├── config_registry.yaml     # 版本注册表
└── config_history.yaml     # 配置变更历史

src/core/
├── config_manager.py        # 核心模块
├── version_registry.py     # 版本注册
├── version_checker.py     # 版本检查
├── config_watcher.py      # 配置监听
├── config_cli.py          # CLI命令
└── exceptions.py          # 异常定义
```

---

## 九、工时估算

| 功能 | 工时 |
|------|------|
| ConfigRegistry核心（全局+本地） | 4h |
| VersionChecker | 3h |
| ConfigWatcher | 3h |
| **Skill版本管理** | **3h** |
| **跨项目同步** | **3h** |
| CLI命令（扩展版） | 3h |
| 与现有模块集成 | 4h |
| 测试 | 3h |
| **总计** | **~26h** |

---

## 十、下一步

1. **创建全局配置目录** (`~/.config/opencode/`)
2. **实现ConfigRegistry类**（支持全局+本地）
3. **实现SkillVersionManager**
4. **实现ProjectSyncManager**
5. **集成到skill_enforcer**
6. **集成到todowrite**
7. **添加扩展版CLI命令**

---

**作者**: Consultant  
**日期**: 2026-02-17
