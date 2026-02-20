# TODO拆分与代码重构计划

## 背景

当前代码库存在严重的紧耦合问题，影响可维护性和可测试性。

## 当前TODO相关文件结构

```
src/core/todo_*.py          # 7个核心模块
src/cli/todo_commands.py     # CLI命令
src/cli/check_todo_on_startup.py  # 启动检查
```

### 依赖关系图 (34处引用)

```
todo_storage.py          ← 9个模块依赖
todo_sync_manager.py    ← 5个模块依赖
todo_queue_manager.py   ← 7个模块依赖
todo_id_generator.py    ← 1个模块依赖
todo_template.py        ← 0个模块依赖
todo_migrator.py        ← 0个模块依赖
auto_todo_creator.py    ← 0个模块依赖
```

## 紧耦合问题表现

1. **硬编码路径依赖**: 大量模块需要 `project_path` 参数才能初始化
2. **环境依赖**: `GitMonitor`, `GitSync` 等需要 Git 仓库环境
3. **隐藏依赖**: 很多类在 `__init__` 中隐式依赖配置文件或数据库
4. **测试困难**: 由于耦合度高，单元测试覆盖率难以提升

## 单元测试进度

### 当前覆盖率
- **测试通过**: 2552 个
- **代码覆盖率**: 64%

### 新增测试文件
1. `tests/test_utils.py` - 32 个测试 (utils模块: 100%)
2. `tests/test_cli_modules.py` - 18 个测试 (CLI模块)
3. `tests/test_supplement_core.py` - 14 个测试

### 无法继续提升的原因
- 大量模块需要特定初始化参数 (`project_path`)
- 许多类需要 Git 仓库环境
- 复杂的内部依赖导致难以 mock

## 重构建议

### 1. 依赖注入模式

```python
# 当前 (紧耦合)
class GitMonitor:
    def __init__(self, project_path):
        self.git = Git(project_path)  # 内部创建

# 改进 (松耦合)
class GitMonitor:
    def __init__(self, git: Git):
        self.git = git  # 外部注入
```

### 2. 接口抽象

定义抽象基类，便于测试时 mock：
- `ITodoStorage`
- `IGitOperations`
- `IConfigProvider`

### 3. 配置外部化

使用配置对象统一管理路径和依赖：
```python
class AppConfig:
    def __init__(self, project_path: str):
        self.project_path = project_path
        self.todo_db_path = f"{project_path}/state/todos.db"
```

### 4. 工厂模式

创建模块时使用工厂方法：
```python
class TodoModuleFactory:
    @staticmethod
    def create_storage(config: AppConfig) -> ITodoStorage:
        return TodoStorage(config.todo_db_path)
    
    @staticmethod
    def create_sync_manager(storage: ITodoStorage) -> TodoSyncManager:
        return TodoSyncManager(storage)
```

## TODO拆分方案

### 方案: 按职责拆分

```
src/core/todo/
├── storage.py          # 数据持久化 (ITodoStorage)
├── sync.py             # 同步逻辑 (TodoSyncManager)
├── queue.py            # 队列管理 (TodoQueueManager)
├── commands.py         # CLI命令
├── templates.py        # 模板
├── migrator.py        # 迁移
├── id_generator.py    # ID生成
└── __init__.py        # 统一导出
```

### 实施步骤

1. **创建抽象接口** - 定义 `ITodoStorage`, `ITodoQueue` 等接口
2. **重构存储层** - 依赖注入，移除硬编码路径
3. **重构业务层** - 使用接口而非具体类
4. **拆分CLI** - 将命令移到独立模块
5. **更新依赖引用** - 修改34处引用
6. **编写测试** - 重构后编写单元测试

## 未完成事项

1. ⏳ 代码覆盖率未达到80% (当前64%)
2. ⏳ TODO模块紧耦合重构
3. ⏳ 34处todo相关导入需要更新

## 相关文档

- `docs/07-research/RESEARCH_YAML_REFERENCE_ANALYSIS.md` - YAML引用分析
