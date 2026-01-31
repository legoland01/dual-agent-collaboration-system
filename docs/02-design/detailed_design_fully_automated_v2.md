# 双Agent全自动协作框架详细设计文档

## 版本信息

- **版本**：v2
- **关联需求版本**：v2
- **创建日期**：2026-01-31
- **作者**：Agent 2（开发）
- **关联需求文档**：`docs/01-requirements/requirements_fully_automated_v2.md`

## 1. 系统架构概述

### 1.1 整体架构设计

全自动Agent协作框架采用分层架构设计，将系统划分为表示层、Agent核心层、基础设施层和外部服务层四个主要层次。这种分层设计的核心目标是实现高度解耦的系统架构，使得各个组件可以独立开发、测试和维护，同时保证系统整体的可靠性和可扩展性。表示层负责与用户交互，包括命令行界面和状态显示；Agent核心层是整个系统的大脑，包含状态检测、行为决策和任务执行等核心逻辑；基础设施层提供状态管理、Git操作、文档生成等基础能力；外部服务层则封装了与Gitee、GitHub等外部系统的交互接口。

系统的核心设计理念是"事件驱动、自治协作"。两个Agent通过Git仓库进行异步通信，不建立直接的Socket连接或消息队列，这种设计极大地简化了系统架构，同时保证了通信的可靠性和可追溯性。每个Agent都具备完整的自主行为能力，能够根据当前状态自主决定应该执行的操作，无需人工干预。Agent之间通过状态文件和文档变更来感知对方的工作进展，从而协调各自的行动。整个系统的运行遵循预定义的状态机模型，确保协作流程的有序推进。

在技术选型方面，系统继续沿用Python作为主要开发语言，充分利用Python在脚本处理、系统集成和快速开发方面的优势。Git操作采用subprocess方式直接调用Git命令，避免了对GitPython库的依赖，提高了系统的兼容性和稳定性。状态管理继续使用YAML文件格式，保持与现有系统的一致性。CLI界面采用Click框架实现，提供友好的命令行交互体验。整个系统的代码组织遵循模块化原则，每个功能模块都有清晰的职责边界和标准化的接口定义。

### 1.2 Agent核心组件架构

每个Agent由六个核心组件构成，这些组件协同工作，实现Agent的自主行为能力。Git Monitor组件负责持续监控远程仓库的变化，通过定期轮询或Webhook方式检测新的提交、文档更新和状态变更。Brain Engine是Agent的决策中枢，它根据当前状态、预定义规则和外部信号决定应该执行什么操作。Task Executor负责具体任务的执行，包括文档编写、代码开发、测试执行等。Doc Generator专门处理文档的自动生成，根据模板和上下文信息生成各类项目文档。Tester组件负责测试相关工作，包括白盒测试和黑盒测试的执行与报告。Deployer组件处理部署相关任务，包括打包、部署和验证。

这六个组件之间的关系可以用数据流来描述：Git Monitor持续检测外部变化，将检测到的变更信息传递给Brain Engine；Brain Engine根据变更信息和当前状态，决定需要执行的任务类型和参数，然后将任务描述传递给Task Executor；Task Executor根据任务类型调用Doc Generator、Tester或Deployer执行具体操作；执行完成后，Task Executor将结果反馈给Brain Engine，Brain Engine更新内部状态并决定下一步行动；同时，所有操作都会通过Git Helper提交到远程仓库，供另一个Agent感知。这种闭环的数据流设计确保了Agent行为的连续性和一致性。

组件间的通信采用事件机制实现解耦。当Git Monitor检测到变化时，它发布一个事件；Brain Engine订阅这些事件，并根据事件类型触发相应的处理逻辑。这种发布-订阅模式的好处是组件之间不需要直接引用，降低了耦合度，同时便于扩展新的事件类型和处理逻辑。例如，当需要增加新的触发条件时，只需在Git Monitor中添加相应的事件发布代码，Brain Engine中添加对应的事件处理逻辑即可，不需要修改其他组件的代码。

## 2. 核心模块详细设计

### 2.1 Git Monitor模块设计

Git Monitor是Agent感知外部世界的窗口，它的设计直接影响到系统的响应速度和资源消耗。Git Monitor采用两种工作模式：轮询模式和Webhook模式。轮询模式是默认模式，Agent定期执行git fetch命令获取远程仓库的最新状态，然后与本地状态进行对比，识别出新增的提交、修改的文件和状态变更。Webhook模式是可选模式，需要用户在Gitee配置Webhook地址，当仓库发生变更时，Gitee主动向Agent发送通知，Agent收到通知后立即进行状态检测。Webhook模式可以实现近实时的响应，但需要额外的配置工作。

轮询配置采用自适应策略，初始间隔为30秒，当检测到有活动发生时，间隔会临时缩短以加快响应速度；当持续一段时间没有变化时，间隔会逐渐延长，最长不超过5分钟，这就是指数退避机制。退避因子为1.5，即每次延长间隔时都乘以1.5。这种自适应的轮询策略可以在响应速度和资源消耗之间取得平衡，既能及时响应变更，又不会对Git服务器造成过大压力。

Git Monitor的核心检测逻辑包括以下几个步骤：首先执行git fetch更新远程引用；然后比较本地和远程的commit差异，识别新增的提交；接着检查新增提交中是否包含特定类型的文件（如需求文档、设计文档、测试用例等）；最后根据文件类型触发相应的事件。为了提高检测效率，Git Monitor会维护一个本地索引，记录已处理的提交SHA，下次检测时跳过这些已处理的提交。这个索引会在每次成功处理后更新，确保不会遗漏任何变更。

```python
class GitMonitor:
    """Git监控器组件。"""
    
    def __init__(self, project_path: str, agent_id: str):
        self.project_path = Path(project_path)
        self.agent_id = agent_id
        self.processed_commits = set()
        self.last_fetch_time = None
        self.polling_config = {
            "interval": 30,
            "timeout": 3600,
            "max_retries": 3,
            "debounce": 5,
            "backoff_factor": 1.5,
            "max_interval": 300
        }
    
    def detect_changes(self) -> List[Dict[str, Any]]:
        """检测远程变更。"""
        changes = []
        try:
            self._fetch_remote()
            new_commits = self._get_new_commits()
            for commit in new_commits:
                commit_changes = self._analyze_commit(commit)
                if commit_changes:
                    changes.extend(commit_changes)
                self.processed_commits.add(commit["sha"])
        except Exception as e:
            self._handle_error(e)
        return changes
    
    def _fetch_remote(self) -> None:
        """获取远程引用。"""
        result = subprocess.run(
            ["git", "fetch"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            raise GitFetchError(f"Git fetch failed: {result.stderr}")
    
    def _get_new_commits(self) -> List[Dict[str, Any]]:
        """获取新增的提交。"""
        result = subprocess.run(
            ["git", "log", "--since=last_fetch", "--oneline"],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        commits = []
        for line in result.stdout.strip().split("\n"):
            if line:
                sha = line.split()[0]
                if sha not in self.processed_commits:
                    commits.append({
                        "sha": sha,
                        "message": line[len(sha)+1:]
                    })
        return commits
    
    def _analyze_commit(self, commit: Dict[str, str]) -> List[Dict[str, Any]]:
        """分析单个提交，识别变更类型。"""
        changes = []
        # 检查文件变更
        result = subprocess.run(
            ["git", "show", "--stat", "--name-only", commit["sha"]],
            cwd=self.project_path,
            capture_output=True,
            text=True
        )
        files = self._parse_changed_files(result.stdout)
        
        # 识别变更类型
        if self._is_requirements_doc(files):
            changes.append({
                "type": "requirements_created",
                "files": files,
                "commit": commit
            })
        elif self._is_review_doc(files):
            changes.append({
                "type": "review_updated",
                "files": files,
                "commit": commit
            })
        elif self._is_design_doc(files):
            changes.append({
                "type": "design_created",
                "files": files,
                "commit": commit
            })
        elif self._is_code_changed(files):
            changes.append({
                "type": "code_updated",
                "files": files,
                "commit": commit
            })
        elif self._is_test_case(files):
            changes.append({
                "type": "test_case_created",
                "files": files,
                "commit": commit
            })
        elif self._is_bug_report(files):
            changes.append({
                "type": "bug_report_created",
                "files": files,
                "commit": commit
            })
        
        return changes
```

### 2.2 Brain Engine模块设计

Brain Engine是Agent的决策中枢，负责根据当前状态和外部信号决定应该执行什么操作。Brain Engine采用规则引擎和状态机相结合的设计模式：状态机定义了系统可能的全部状态以及状态之间的转换规则；规则引擎则根据当前状态和触发条件，判断是否应该触发状态转换以及执行什么操作。这种设计的优势在于规则的表达能力强，可以处理复杂的业务逻辑；同时状态机提供了清晰的执行框架，确保所有操作都在正确的时机执行。

Brain Engine的核心数据结构是一个规则库和状态机实例。规则库是一个优先级的规则列表，每条规则包含触发条件（什么样的外部事件或状态变化）和对应的动作（应该执行什么操作）。规则按优先级排序，高优先级的规则先匹配。状态机实例维护当前状态信息，提供状态查询和状态转换的功能。Brain Engine的主循环持续运行，不断检测外部变化，对变化进行规则匹配，触发相应的动作，更新状态机状态。

规则定义采用声明式语法，便于理解和维护。每条规则由条件部分和动作部分组成。条件部分是一个函数，返回布尔值，表示是否满足触发条件。动作部分是一个函数，包含具体的执行逻辑。这种设计使得非开发人员也能理解和修改业务规则，只需遵循既定的接口规范即可。规则库支持动态加载，可以在运行时添加、删除或修改规则，无需重启系统。

```python
class BrainEngine:
    """Agent决策引擎。"""
    
    def __init__(self, agent_id: str, state_manager, git_helper):
        self.agent_id = agent_id
        self.state_manager = state_manager
        self.git_helper = git_helper
        self.rules = []
        self.state_machine = self._create_state_machine()
        self._load_rules()
    
    def _create_state_machine(self) -> StateMachine:
        """创建状态机。"""
        return StateMachine(
            states=[
                "project_init", "requirements_draft", "requirements_review",
                "requirements_approved", "design_draft", "design_review",
                "design_approved", "development", "testing", "deployment",
                "completed", "paused"
            ],
            transitions=self._define_transitions(),
            initial_state="project_init"
        )
    
    def _define_transitions(self) -> Dict[str, Dict[str, str]]:
        """定义状态转换规则。"""
        return {
            "project_init": {"next": "requirements_draft", "condition": "agent1_active"},
            "requirements_draft": {"next": "requirements_review", "condition": "requirements_created"},
            "requirements_review": {"next": "requirements_approved", "condition": "both_signed"},
            "requirements_approved": {"next": "design_draft", "condition": "agent2_active"},
            "design_draft": {"next": "design_review", "condition": "design_created"},
            "design_review": {"next": "design_approved", "condition": "both_signed"},
            "design_approved": {"next": "development", "condition": "agent2_active"},
            "development": {"next": "testing", "condition": "code_committed"},
            "testing": {"next": "deployment", "condition": "test_passed"},
            "deployment": {"next": "completed", "condition": "deployed"}
        }
    
    def _load_rules(self) -> None:
        """加载行为规则。"""
        if self.agent_id == "agent1":
            self.rules = [
                Rule(
                    name="create_requirements",
                    condition=self._is_project_init,
                    action=self._create_requirements,
                    priority=1
                ),
                Rule(
                    name="signoff_requirements",
                    condition=self._requirements_review_ready,
                    action=self._signoff_requirements,
                    priority=2
                ),
                Rule(
                    name="review_design",
                    condition=self._design_created,
                    action=self._review_design,
                    priority=3
                ),
                Rule(
                    name="blackbox_test",
                    condition=self._code_committed,
                    action=self._execute_blackbox_test,
                    priority=4
                ),
                Rule(
                    name="deploy_system",
                    condition=self._test_passed,
                    action=self._execute_deployment,
                    priority=5
                )
            ]
        else:
            self.rules = [
                Rule(
                    name="review_requirements",
                    condition=self._requirements_created,
                    action=self._review_requirements,
                    priority=1
                ),
                Rule(
                    name="signoff_requirements",
                    condition=self._pm_signed,
                    action=self._signoff_requirements,
                    priority=2
                ),
                Rule(
                    name="create_design",
                    condition=self._requirements_approved,
                    action=self._create_design,
                    priority=3
                ),
                Rule(
                    name="implement_code",
                    condition=self._design_approved,
                    action=self._implement_code,
                    priority=4
                ),
                Rule(
                    name="fix_bugs",
                    condition=self._bug_reported,
                    action=self._fix_bugs,
                    priority=5
                )
            ]
    
    def process_events(self, events: List[Dict[str, Any]]) -> List[ActionResult]:
        """处理外部事件，执行相应动作。"""
        results = []
        state = self.state_manager.load_state()
        
        for event in events:
            for rule in self.rules:
                if rule.condition(state, event):
                    try:
                        result = rule.action(state, event)
                        results.append(result)
                        self._update_state(state, event, result)
                    except Exception as e:
                        results.append(ActionResult(
                            success=False,
                            error=str(e),
                            rule=rule.name
                        ))
                    break
        
        return results
    
    def decide_next_action(self) -> Optional[Dict[str, Any]]:
        """根据当前状态决定下一步动作。"""
        state = self.state_manager.load_state()
        current_phase = state.get("phase", "")
        
        # 根据当前阶段和Agent类型决定动作
        if self.agent_id == "agent1":
            return self._decide_agent1_action(current_phase, state)
        else:
            return self._decide_agent2_action(current_phase, state)
```

### 2.3 Task Executor模块设计

Task Executor负责具体任务的执行，它是Agent行为的具体实现者。Task Executor采用策略模式设计，每种任务类型对应一个具体的执行策略。这种设计的优势在于新增任务类型时只需添加新的策略类，无需修改现有代码，符合开闭原则。Task Executor维护一个策略注册表，根据任务类型查找对应的执行策略，然后调用策略的execute方法执行任务。

任务执行的生命周期包括准备、执行、验证和提交四个阶段。准备阶段进行参数验证和前置条件检查；执行阶段调用具体的执行逻辑；验证阶段检查执行结果是否符合预期；提交阶段将变更提交到Git仓库。每个阶段都有完善的错误处理机制，异常情况会被捕获并转换为标准化的错误信息，供上层组件处理。任务执行支持超时控制，每个任务都有默认的超时时间，超时后会强制终止并返回超时错误。

任务执行支持重试机制。当任务执行失败时，如果失败原因是可以恢复的（如网络临时中断），Task Executor会自动进行重试，重试次数由max_retries参数控制。重试采用指数退避策略，第一次重试立即执行，之后每次重试的间隔时间翻倍。如果重试次数用尽仍然失败，任务会标记为需要人工处理，同时发送通知提醒相关人员。

```python
class TaskExecutor:
    """任务执行器。"""
    
    def __init__(self, project_path: str, git_helper, state_manager):
        self.project_path = Path(project_path)
        self.git_helper = git_helper
        self.state_manager = state_manager
        self.strategies = {}
        self._register_strategies()
    
    def _register_strategies(self) -> None:
        """注册任务执行策略。"""
        self.strategies["create_requirements"] = CreateRequirementsStrategy()
        self.strategies["review_requirements"] = ReviewRequirementsStrategy()
        self.strategies["create_design"] = CreateDesignStrategy()
        self.strategies["implement_code"] = ImplementCodeStrategy()
        self.strategies["execute_tests"] = ExecuteTestsStrategy()
        self.strategies["fix_bugs"] = FixBugsStrategy()
        self.strategies["deploy_system"] = DeploySystemStrategy()
    
    def execute(self, task_type: str, task_data: Dict[str, Any]) -> ActionResult:
        """执行任务。"""
        strategy = self.strategies.get(task_type)
        if not strategy:
            return ActionResult(
                success=False,
                error=f"Unknown task type: {task_type}"
            )
        
        try:
            # 准备阶段
            if not strategy.validate(task_data):
                return ActionResult(
                    success=False,
                    error="Task validation failed"
                )
            
            # 执行阶段
            result = strategy.execute(task_data)
            
            # 验证阶段
            if result.success:
                if not strategy.verify(result):
                    return ActionResult(
                        success=False,
                        error="Task verification failed"
                    )
            
            # 提交阶段
            if result.success and task_data.get("should_commit", True):
                self._commit_changes(result)
            
            return result
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=str(e),
                task_type=task_type
            )
    
    def _commit_changes(self, result: ActionResult) -> None:
        """提交变更到Git。"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"feat({self.state_manager.get_current_phase()}): {result.message} - {timestamp}"
        self.git_helper.push(message)


class BaseStrategy(ABC):
    """任务执行策略基类。"""
    
    @abstractmethod
    def validate(self, task_data: Dict[str, Any]) -> bool:
        """验证任务参数。"""
        pass
    
    @abstractmethod
    def execute(self, task_data: Dict[str, Any]) -> ActionResult:
        """执行任务。"""
        pass
    
    def verify(self, result: ActionResult) -> bool:
        """验证执行结果。"""
        return result.success


class CreateRequirementsStrategy(BaseStrategy):
    """创建需求文档策略。"""
    
    def validate(self, task_data: Dict[str, Any]) -> bool:
        return "project_name" in task_data
    
    def execute(self, task_data: Dict[str, Any]) -> ActionResult:
        project_name = task_data["project_name"]
        template = task_data.get("template", "requirements_TEMPLATE.md")
        
        # 生成需求文档
        doc_content = self._generate_requirements_doc(project_name, template)
        doc_path = f"docs/01-requirements/requirements_{project_name}_v1.md"
        
        with open(doc_path, "w", encoding="utf-8") as f:
            f.write(doc_content)
        
        return ActionResult(
            success=True,
            message=f"Created requirements document: {doc_path}",
            files_created=[doc_path]
        )
    
    def _generate_requirements_doc(self, project_name: str, template: str) -> str:
        """生成需求文档内容。"""
        template_path = Path(template)
        if template_path.exists():
            with open(template_path, "r", encoding="utf-8") as f:
                content = f.read()
            content = content.replace("{{project_name}}", project_name)
            content = content.replace("{{date}}", datetime.now().strftime("%Y-%m-%d"))
            return content
        return f"# {project_name}\n\n## 项目概述\n\n## 功能需求\n\n## 非功能需求\n"
```

### 2.4 状态机设计

状态机是系统行为的核心框架，它定义了系统可能处于的所有状态以及状态之间的转换规则。状态机的设计采用确定性有限自动机（DFA）模型，每个状态在给定输入下有唯一确定的下一个状态。这种设计的优势是行为可预测、易于调试，适合需要高度可靠性的协作场景。状态机支持嵌套状态和并发状态，可以表达复杂的业务流程。

状态机的核心数据结构包括状态集合、转换规则集合和当前状态。状态集合定义了系统所有可能的状态；转换规则定义了从一个状态到另一个状态的条件和动作；当前状态记录系统当前所处的状态。状态机提供状态查询、状态转换、状态历史回溯等方法。状态转换是原子的，要么完全成功，要么保持原状态不变，不会出现中间状态。

状态机与Brain Engine紧密配合。Brain Engine根据外部事件触发状态转换，状态机负责验证转换的合法性并执行转换动作。状态转换可能触发副作用，如更新状态文件、发送通知等。这些副作用通过回调函数实现，状态机提供一个register_callback方法，允许注册状态转换时的回调函数。回调函数按照注册顺序依次执行，返回值为True表示继续执行，返回False表示中断后续回调。

```python
class StateMachine:
    """状态机。"""
    
    def __init__(self, states: List[str], transitions: Dict[str, Dict[str, str]], 
                 initial_state: str):
        self.states = set(states)
        self.transitions = transitions
        self.current_state = initial_state
        self.history = [initial_state]
        self.callbacks = defaultdict(list)
    
    def get_current_state(self) -> str:
        """获取当前状态。"""
        return self.current_state
    
    def can_transition(self, to_state: str) -> bool:
        """检查是否可以转换到指定状态。"""
        if to_state not in self.states:
            return False
        transition = self.transitions.get(self.current_state, {})
        return transition.get("next") == to_state
    
    def transition(self, to_state: str, context: Dict[str, Any] = None) -> bool:
        """执行状态转换。"""
        if not self.can_transition(to_state):
            return False
        
        old_state = self.current_state
        self.current_state = to_state
        self.history.append(to_state)
        
        # 执行回调
        for callback in self.callbacks[old_state]:
            if not callback(to_state, context):
                break
        
        return True
    
    def get_valid_next_states(self) -> List[str]:
        """获取合法的下一状态列表。"""
        transition = self.transitions.get(self.current_state, {})
        next_state = transition.get("next")
        if next_state:
            return [next_state]
        return []
    
    def register_callback(self, state: str, callback: Callable) -> None:
        """注册状态转换回调。"""
        self.callbacks[state].append(callback)
    
    def get_state_progress(self) -> Dict[str, Any]:
        """获取状态进度信息。"""
        state_order = [
            "project_init", "requirements_draft", "requirements_review",
            "requirements_approved", "design_draft", "design_review",
            "design_approved", "development", "testing", "deployment",
            "completed"
        ]
        try:
            current_index = state_order.index(self.current_state)
            total = len(state_order) - 1
            return {
                "current_state": self.current_state,
                "progress_percentage": (current_index / total) * 100,
                "remaining_states": state_order[current_index + 1:]
            }
        except ValueError:
            return {
                "current_state": self.current_state,
                "progress_percentage": 0,
                "remaining_states": []
            }
```

### 2.5 文档生成器设计

文档生成器负责根据模板和上下文信息自动生成各类项目文档。文档生成器采用模板引擎模式，支持Jinja2模板渲染。系统预设了六类文档模板：需求文档模板、设计文档模板、测试用例模板、Bug报告模板、测试报告模板和部署报告模板。每个模板定义了文档的标准结构和占位符，文档生成时只需填充占位符即可。模板支持条件渲染和循环结构，可以生成复杂格式的文档。

文档生成流程包括模板选择、上下文准备、变量填充和格式检查四个步骤。模板选择根据任务类型确定使用哪个模板；上下文准备从状态文件和任务数据中提取模板所需的信息；变量填充使用Jinja2引擎将上下文数据填充到模板中；格式检查验证生成的文档是否符合模板规范，不符合则重新生成或标记为需要人工审核。文档生成支持质量检查，可以配置检查规则，如文档长度、必填字段、格式规范等。

文档生成器支持自定义模板，用户可以添加新的模板文件到templates目录。模板文件的命名规则为`{document_type}_TEMPLATE.md`，系统启动时会自动扫描templates目录，加载所有模板文件。模板文件支持变量替换、条件渲染和循环结构，语法遵循Jinja2规范。系统还提供模板调试功能，可以在开发阶段测试模板渲染效果，确保模板正确无误。

```python
class DocGenerator:
    """文档生成器。"""
    
    TEMPLATE_DIR = "templates"
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.template_dir = self.project_path / self.TEMPLATE_DIR
        self.template_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        self.quality_checker = QualityChecker()
    
    def generate(self, doc_type: str, context: Dict[str, Any]) -> ActionResult:
        """生成文档。"""
        template_name = f"{doc_type}_TEMPLATE.md"
        
        try:
            template = self.template_env.get_template(template_name)
            content = template.render(**context)
            
            # 质量检查
            check_result = self.quality_checker.check(content, doc_type)
            if not check_result.passed:
                # 如果质量检查不通过，尝试重新生成或标记为需审核
                if context.get("retry_count", 0) < 3:
                    context["retry_count"] = context.get("retry_count", 0) + 1
                    return self.generate(doc_type, context)
                else:
                    return ActionResult(
                        success=False,
                        error=f"Quality check failed: {check_result.errors}",
                        quality_issues=check_result.errors
                    )
            
            # 生成文档路径
            doc_path = self._generate_doc_path(doc_type, context)
            
            # 写入文件
            with open(doc_path, "w", encoding="utf-8") as f:
                f.write(content)
            
            return ActionResult(
                success=True,
                message=f"Generated {doc_type} document",
                files_created=[doc_path],
                quality_score=check_result.score
            )
            
        except TemplateNotFound:
            # 如果找不到模板，使用默认模板
            return self._generate_default_doc(doc_type, context)
        except Exception as e:
            return ActionResult(
                success=False,
                error=str(e)
            )
    
    def _generate_doc_path(self, doc_type: str, context: Dict[str, Any]) -> str:
        """生成文档路径。"""
        path_map = {
            "requirements": "docs/01-requirements/requirements_{project}_{version}.md",
            "requirements_review": "docs/01-requirements/requirements_{project}_review_{version}.md",
            "design": "docs/02-design/detailed_design_{project}_{version}.md",
            "design_review": "docs/02-design/design_{project}_review_{version}.md",
            "test_case": "docs/03-test/test_case_{project}_{version}.md",
            "test_report": "docs/03-test/test_report_{project}_{version}.md",
            "bug_report": "docs/03-test/bug_report_{project}_{version}.md",
            "deployment_report": "docs/04-deployment/deployment_report_{version}.md"
        }
        
        path_template = path_map.get(doc_type, "docs/{doc_type}_{project}_{version}.md")
        project = context.get("project_name", "unknown")
        version = context.get("version", "v1")
        
        return path_template.format(doc_type=doc_type, project=project, version=version)


class QualityChecker:
    """文档质量检查器。"""
    
    def __init__(self):
        self.rules = self._default_rules()
    
    def _default_rules(self) -> List[QualityRule]:
        """默认质量检查规则。"""
        return [
            MinLengthRule(min_length=100),
            RequiredFieldsRule(fields=["# ", "## "]),
            NoBrokenLinksRule(),
            ConsistentFormattingRule()
        ]
    
    def check(self, content: str, doc_type: str) -> QualityResult:
        """执行质量检查。"""
        errors = []
        score = 100
        
        for rule in self.rules:
            if not rule.check(content):
                errors.append(rule.error_message)
                score -= rule.penalty
        
        return QualityResult(
            passed=score >= 60,
            score=max(0, score),
            errors=errors
        )
```

### 2.6 异常处理机制设计

异常处理机制是保障系统稳定运行的关键组件。系统定义了完善的异常分类体系和对应的处理策略。异常分为可恢复异常和不可恢复异常两大类。可恢复异常包括网络超时、Git冲突（轻微）、临时文件缺失等，这类异常可以通过重试或回退操作恢复；不可恢复异常包括权限不足、磁盘空间不足、状态文件损坏（严重）等，这类异常需要人工干预才能解决。

异常处理采用分级策略。系统级异常（如磁盘空间不足）会立即终止运行并记录日志；操作级异常（如单个任务执行失败）会触发重试机制；业务级异常（如状态不合法）会暂停当前流程并等待人工处理。每种异常都有标准化的错误码和错误信息，便于问题定位和用户通知。异常处理还包括现场保存机制，发生异常时会保存当前状态、执行上下文和错误信息，支持后续恢复或问题排查。

```python
class ExceptionHandler:
    """异常处理器。"""
    
    def __init__(self, state_manager, notifier):
        self.state_manager = state_manager
        self.notifier = notifier
        self.recovery_strategies = {
            "retryable": self._handle_retryable_exception,
            "recoverable": self._handle_recoverable_exception,
            "fatal": self._handle_fatal_exception
        }
    
    def handle(self, exception: Exception, context: Dict[str, Any] = None) -> ExceptionResult:
        """处理异常。"""
        exception_type = self._classify_exception(exception)
        
        # 保存现场
        self._save_context(exception, context)
        
        # 根据异常类型选择处理策略
        handler = self.recovery_strategies.get(exception_type, self._handle_unknown_exception)
        return handler(exception, context)
    
    def _classify_exception(self, exception: Exception) -> str:
        """分类异常。"""
        if isinstance(exception, (GitConflictError, TimeoutError)):
            return "retryable"
        elif isinstance(exception, (StateCorruptedError, FileNotFoundError)):
            return "recoverable"
        elif isinstance(exception, (PermissionError, DiskFullError)):
            return "fatal"
        return "unknown"
    
    def _handle_retryable_exception(self, exception: Exception, context: Dict[str, Any]) -> ExceptionResult:
        """处理可重试异常。"""
        max_retries = context.get("max_retries", 3) if context else 3
        current_retry = context.get("retry_count", 0) if context else 0
        
        if current_retry < max_retries:
            return ExceptionResult(
                handled=True,
                action="retry",
                message=f"Will retry ({current_retry + 1}/{max_retries})",
                next_retry=True
            )
        else:
            return ExceptionResult(
                handled=True,
                action="pause",
                message="Max retries reached, pausing for manual intervention",
                requires_manual=True
            )
    
    def _handle_recoverable_exception(self, exception: Exception, context: Dict[str, Any]) -> ExceptionResult:
        """处理可恢复异常。"""
        return ExceptionResult(
            handled=True,
            action="rollback",
            message=f"Attempting recovery: {str(exception)}",
            requires_manual=False
        )
    
    def _handle_fatal_exception(self, exception: Exception, context: Dict[str, Any]) -> ExceptionResult:
        """处理致命异常。"""
        self.notifier.notify(f"Fatal error: {str(exception)}")
        return ExceptionResult(
            handled=True,
            action="terminate",
            message=f"System terminated: {str(exception)}",
            requires_manual=True
        )
    
    def _save_context(self, exception: Exception, context: Dict[str, Any]) -> None:
        """保存异常现场。"""
        state = self.state_manager.load_state()
        crash_info = {
            "timestamp": datetime.now().isoformat(),
            "exception_type": type(exception).__name__,
            "exception_message": str(exception),
            "current_state": state,
            "context": context
        }
        
        crash_log_path = "state/crash_log.yaml"
        with open(crash_log_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(crash_info, f, allow_unicode=True)
```

## 3. 数据结构设计

### 3.1 状态文件结构

状态文件是系统数据的核心载体，采用YAML格式存储。状态文件分为三个部分：基础信息、阶段信息和元数据。基础信息包含项目名称、类型、创建时间等；阶段信息包含各个阶段的状态、签署状态、版本号等；元数据包含当前Agent、轮询间隔、是否全自动模式等。状态文件的设计遵循向后兼容原则，新增字段都使用默认值填充，不会影响旧版本的读取。

状态文件的读写采用乐观锁机制。每次读取时记录文件的版本号（可以理解为修改次数），写入前再次读取文件，如果版本号变化则说明有其他Agent修改过，需要重新读取并合并。写入操作使用临时文件，完成后重命名，确保写入操作的原子性。这种设计可以有效防止并发写入导致的数据损坏。

```yaml
# state/project_state.yaml
version: "2.0.0"

project:
  name: "双Agent协作项目"
  type: "PYTHON"
  created_at: "2026-01-31T10:00:00"
  updated_at: "2026-01-31T10:30:00"

phase: "requirements_review"

agents:
  agent1:
    role: "产品经理"
    current: true
    status: "active"
  agent2:
    role: "开发"
    current: false
    status: "idle"

requirements:
  version: "v1"
  status: "review"
  pm_signoff: true
  dev_signoff: false
  review_cycles: 1
  review_comments: []

design:
  version: ""
  status: "pending"
  pm_signoff: false
  dev_signoff: false

test:
  version: ""
  status: "pending"
  blackbox_cases: 0
  blackbox_passed: 0
  bug_reports: []

development:
  status: "pending"
  branch: "main"
  last_updated: ""

deployment:
  status: "pending"
  version: ""
  last_updated: ""

metadata:
  current_agent: "agent1"
  auto_mode: true
  polling_interval: 30
  last_sync: "2026-01-31T10:25:00"
  execution_mode: "auto"  # auto/manual

history:
  - timestamp: "2026-01-31T10:00:00"
    agent: "agent1"
    action: "init"
    details: "项目初始化"
  - timestamp: "2026-01-31T10:15:00"
    agent: "agent1"
    action: "create_requirements"
    details: "创建需求文档"
  - timestamp: "2026-01-31T10:20:00"
    agent: "agent2"
    action: "review_requirements"
    details: "评审需求文档"
```

### 3.2 事件数据结构

事件是Agent之间通信的基本单元，每个事件包含事件类型、触发时间、关联文件、源Agent和上下文信息。事件的设计遵循简洁原则，只包含必要的信息，减少传输和处理开销。事件支持序列化，可以持久化存储到事件日志中，便于问题排查和流程追溯。

```python
@dataclass
class AgentEvent:
    """Agent事件。"""
    event_type: str  # 事件类型：requirements_created, review_updated, code_committed等
    timestamp: str  # ISO格式时间戳
    agent_id: str  # 触发事件的Agent ID
    project_path: str  # 项目路径
    commit_sha: str  # 关联的commit SHA
    files: List[str]  # 变更的文件列表
    context: Dict[str, Any]  # 额外上下文信息
    metadata: Dict[str, Any]  # 元数据，如版本信息、状态快照等
```

### 3.3 动作结果数据结构

动作结果记录每次动作执行的结果，包含执行状态、消息、生成的文件、消耗的时间和错误信息。动作结果支持链式记录，可以记录动作执行的完整历史。动作结果是系统日志的重要组成部分，通过分析动作结果可以了解系统的运行状况和性能表现。

```python
@dataclass
class ActionResult:
    """动作执行结果。"""
    success: bool  # 是否成功
    message: str  # 结果消息
    error: Optional[str] = None  # 错误信息
    files_created: List[str] = None  # 创建的文件列表
    files_modified: List[str] = None  # 修改的文件列表
    duration: float = None  # 执行耗时（秒）
    quality_score: float = None  # 质量评分
    timestamp: str = None  # 执行完成时间


@dataclass
class ExceptionResult:
    """异常处理结果。"""
    handled: bool  # 是否已处理
    action: str  # 处理动作：retry/rollback/pause/terminate
    message: str  # 处理消息
    requires_manual: bool = False  # 是否需要人工干预
    recovery_info: Dict[str, Any] = None  # 恢复信息
```

## 4. 接口设计

### 4.1 Agent主接口

Agent对外提供两个主要接口：start接口用于启动Agent，stop接口用于停止Agent。启动时需要指定Agent ID、工作模式和轮询间隔等参数。Agent启动后会进入主循环，持续检测外部变化并执行相应动作。停止时Agent会完成当前正在执行的任务，然后优雅退出。

```python
class Agent:
    """Agent主类。"""
    
    def __init__(self, agent_id: str, project_path: str, mode: str = "auto"):
        self.agent_id = agent_id
        self.project_path = Path(project_path)
        self.mode = mode
        self.state_manager = StateManager(project_path)
        self.git_helper = GitHelper(project_path)
        self.git_monitor = GitMonitor(project_path, agent_id)
        self.brain_engine = BrainEngine(agent_id, self.state_manager, self.git_helper)
        self.task_executor = TaskExecutor(project_path, self.git_helper, self.state_manager)
        self.doc_generator = DocGenerator(project_path)
        self.exception_handler = ExceptionHandler(self.state_manager, self._notify)
        self.running = False
    
    def start(self) -> None:
        """启动Agent。"""
        self.running = True
        self._log(f"Agent {self.agent_id} starting in {self.mode} mode...")
        
        try:
            while self.running:
                # 检测外部变化
                events = self.git_monitor.detect_changes()
                
                # 处理事件
                if events:
                    results = self.brain_engine.process_events(events)
                    self._handle_results(results)
                
                # 决定下一步动作
                if self.mode == "auto":
                    action = self.brain_engine.decide_next_action()
                    if action:
                        result = self.task_executor.execute(
                            action["type"],
                            action["data"]
                        )
                        self._handle_single_result(result)
                
                # 轮询间隔
                time.sleep(self.git_monitor.polling_config["interval"])
                
        except KeyboardInterrupt:
            self._log("Received interrupt signal, stopping...")
        finally:
            self.stop()
    
    def stop(self) -> None:
        """停止Agent。"""
        self.running = False
        self._log(f"Agent {self.agent_id} stopped")
    
    def _handle_results(self, results: List[ActionResult]) -> None:
        """处理动作执行结果。"""
        for result in results:
            self._handle_single_result(result)
    
    def _handle_single_result(self, result: ActionResult) -> None:
        """处理单个动作结果。"""
        if not result.success:
            exception_result = self.exception_handler.handle(
                Exception(result.error),
                {"task_result": result}
            )
            self._log(f"Task failed: {result.error}")
        else:
            self._log(f"Task completed: {result.message}")
    
    def _notify(self, message: str) -> None:
        """发送通知。"""
        # 通知实现，可以是日志、邮件、消息等
        print(f"[NOTIFICATION] {message}")
```

### 4.2 配置接口

系统支持通过配置文件和命令行参数两种方式进行配置。配置文件为YAML格式，放在项目根目录的.agent_config文件中。命令行参数的优先级高于配置文件，可以覆盖配置文件中的设置。配置接口提供get和set方法，支持运行时动态修改配置。

```python
@dataclass
class AgentConfig:
    """Agent配置。"""
    agent_id: str = "agent1"
    mode: str = "auto"  # auto/manual
    polling_interval: int = 30
    max_retries: int = 3
    timeout: int = 3600
    webhook_enabled: bool = False
    webhook_url: str = ""
    notification_enabled: bool = True
    log_level: str = "INFO"


class ConfigManager:
    """配置管理器。"""
    
    def __init__(self, config_path: str = ".agent_config"):
        self.config_path = Path(config_path)
        self.config = AgentConfig()
    
    def load(self) -> AgentConfig:
        """加载配置。"""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            for key, value in data.items():
                if hasattr(self.config, key):
                    setattr(self.config, key, value)
        return self.config
    
    def save(self) -> None:
        """保存配置。"""
        data = {
            key: value for key, value in self.config.__dict__.items()
            if not key.startswith("_")
        }
        with open(self.config_path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True)
    
    def update(self, **kwargs) -> None:
        """更新配置。"""
        for key, value in kwargs.items():
            if hasattr(self.config, key):
                setattr(self.config, key, value)
        self.save()
```

## 5. 测试设计

### 5.1 测试策略

测试策略采用分层测试方法，包括单元测试、集成测试和端到端测试三个层次。单元测试覆盖各个组件的核心逻辑，如状态机转换、规则匹配、文档生成等；集成测试覆盖组件之间的交互，如Git Monitor与Brain Engine的交互、Task Executor与Git Helper的交互等；端到端测试覆盖完整的协作流程，模拟真实场景下两个Agent的协作过程。

测试数据管理采用 fixtures 模式。测试 fixtures 包含标准化的项目模板、状态文件、Git仓库快照等，测试时从 fixtures 加载数据，测试后清理。测试 fixtures 存储在 tests/fixtures 目录，按照测试类型和场景组织。测试执行使用 pytest 框架，支持参数化测试和 fixtures 共享。

```python
# tests/conftest.py
import pytest
import tempfile
from pathlib import Path
import shutil

@pytest.fixture
def temp_project():
    """创建临时项目目录。"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

@pytest.fixture
def initialized_project(temp_project):
    """创建已初始化的项目。"""
    # 创建标准目录结构
    (temp_project / "docs/01-requirements").mkdir(parents=True)
    (temp_project / "docs/02-design").mkdir(parents=True)
    (temp_project / "docs/03-test").mkdir(parents=True)
    (temp_project / "docs/04-deployment").mkdir(parents=True)
    (temp_project / "state").mkdir()
    (temp_project / "src").mkdir()
    (temp_project / "tests").mkdir()
    (temp_project / "templates").mkdir()
    
    # 初始化Git仓库
    subprocess.run(["git", "init"], cwd=temp_project, capture_output=True)
    
    # 初始化状态文件
    state = {
        "version": "2.0.0",
        "project": {
            "name": "TestProject",
            "type": "PYTHON",
            "created_at": "2026-01-31"
        },
        "phase": "project_init",
        "agents": {
            "agent1": {"role": "产品经理", "current": True},
            "agent2": {"role": "开发", "current": False}
        },
        "metadata": {"auto_mode": True}
    }
    
    state_path = temp_project / "state/project_state.yaml"
    with open(state_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(state, f, allow_unicode=True)
    
    yield temp_project


class TestGitMonitor:
    """Git Monitor单元测试。"""
    
    def test_detect_new_requirements(self, initialized_project):
        """测试检测新需求文档。"""
        monitor = GitMonitor(str(initialized_project), "agent2")
        
        # 创建需求文档
        req_path = initialized_project01-requirements/ / "docs/requirements_test_v1.md"
        with open(req_path, "w", encoding="utf-8") as f:
            f.write("# Test Requirements\n\n## Overview\n")
        
        # 检测变更
        changes = monitor.detect_changes()
        
        assert len(changes) >= 1
        assert any(c["type"] == "requirements_created" for c in changes)
    
    def test_polling_interval(self, initialized_project):
        """测试轮询间隔配置。"""
        monitor = GitMonitor(str(initialized_project), "agent1")
        
        assert monitor.polling_config["interval"] == 30
        assert monitor.polling_config["max_interval"] == 300
        assert monitor.polling_config["backoff_factor"] == 1.5


class TestStateMachine:
    """状态机单元测试。"""
    
    def test_state_transition(self):
        """测试状态转换。"""
        sm = StateMachine(
            states=["A", "B", "C"],
            transitions={
                "A": {"next": "B"},
                "B": {"next": "C"}
            },
            initial_state="A"
        )
        
        assert sm.get_current_state() == "A"
        assert sm.can_transition("B")
        assert not sm.can_transition("C")
        
        sm.transition("B")
        assert sm.get_current_state() == "B"
    
    def test_progress_calculation(self):
        """测试进度计算。"""
        sm = StateMachine(
            states=["A", "B", "C", "D"],
            transitions={
                "A": {"next": "B"},
                "B": {"next": "C"},
                "C": {"next": "D"}
            },
            initial_state="A"
        )
        
        progress = sm.get_state_progress()
        assert progress["progress_percentage"] == 0
        
        sm.transition("B")
        progress = sm.get_state_progress()
        assert progress["progress_percentage"] == pytest.approx(33.33, rel=0.1)


class TestDocGenerator:
    """文档生成器单元测试。"""
    
    def test_generate_requirements(self, initialized_project):
        """测试生成需求文档。"""
        generator = DocGenerator(str(initialized_project))
        
        result = generator.generate("requirements", {
            "project_name": "TestProject",
            "version": "v1"
        })
        
        assert result.success
        assert len(result.files_created) == 1
        assert "requirements_TestProject_v1.md" in result.files_created[0]
    
    def test_quality_check(self):
        """测试质量检查。"""
        checker = QualityChecker()
        
        # 长度不足
        result = checker.check("Short content", "requirements")
        assert not result.passed
        
        # 正常内容
        result = checker.check(
            "# Test Project\n\n## Overview\n\nTest content.\n" * 5,
            "requirements"
        )
        assert result.passed
```

## 6. 实施计划

### 6.1 开发阶段划分

根据需求文档的规划，整个项目分为六个阶段实现，总工时10天。

第一阶段（2天）聚焦于Agent核心框架的搭建。这一阶段的主要任务是实现Git Monitor组件的完整功能，包括轮询机制、变更检测和事件生成；实现Brain Engine的基本框架，包括状态机基础、规则引擎和事件处理流程；实现Task Executor的任务执行框架，包括策略注册、执行调度和结果处理。这一阶段结束时，Agent应该能够运行并检测到Git仓库的变更，但还不能执行复杂的业务逻辑。

第二阶段（2天）聚焦于状态机的完善。这一阶段的主要任务是实现完整的状态转换逻辑，覆盖协作流程的所有阶段；实现状态持久化，确保系统重启后能够恢复到正确状态；实现状态冲突检测和处理，防止两个Agent同时修改状态文件。这一阶段结束时，状态机应该能够正确处理所有预定义的状态转换场景。

第三阶段（2天）聚焦于Agent行为规则的实现。这一阶段的主要任务是实现Agent 1的所有行为规则，包括需求编写、评审签署、设计评审、黑盒测试和部署上线；实现Agent 2的所有行为规则，包括需求评审、详细设计、代码实现和白盒测试；实现任务执行的具体策略，覆盖各种任务类型。

第四阶段（1天）聚焦于文档生成器的完善。这一阶段的主要任务是实现所有文档模板的生成逻辑；实现文档质量检查机制；实现模板管理和动态加载功能。这一阶段结束时，Agent应该能够自动生成符合规范的各类项目文档。

第五阶段（1天）聚焦于异常处理机制的完善。这一阶段的主要任务是实现完整的异常分类和处理策略；实现现场保存和恢复机制；实现通知和告警功能。这一阶段结束时，系统应该能够优雅地处理各种异常情况。

第六阶段（2天）聚焦于测试验证和优化。这一阶段的主要任务是编写完整的单元测试和集成测试；执行端到端流程测试；根据测试结果进行优化和修复。这一阶段结束时，系统应该通过所有测试，可以进入部署阶段。

### 6.2 里程碑定义

| 里程碑 | 时间 | 验收标准 | 产出 |
|-------|------|---------|------|
| M1: 框架就绪 | 第2天 | Agent核心组件可运行，Git Monitor能检测变更 | 源码、基础测试 |
| M2: 状态机完成 | 第4天 | 状态转换正常执行，无死锁 | 状态机实现、状态管理测试 |
| M3: 行为规则完成 | 第6天 | Agent 1/2行为规则全部实现 | 行为规则实现、集成测试 |
| M4: 文档生成完成 | 第7天 | 文档生成和检查正常 | 文档生成器、模板文件 |
| M5: 异常处理完成 | 第8天 | 异常处理和恢复正常 | 异常处理机制 |
| M6: 发布上线 | 第10天 | 全流程测试通过，部署验证通过 | 可部署包、用户手册 |

## 7. 风险与应对

### 7.1 技术风险

系统实现过程中可能遇到的主要技术风险包括以下几个方面。首先是Git冲突风险，两个Agent同时操作可能导致Git冲突。应对措施包括：使用锁文件机制防止并发执行；在执行Git操作前先拉取最新变更；提供冲突自动合并能力，合并失败时暂停等待人工处理。

其次是状态不一致风险，状态文件可能被意外修改或损坏。应对措施包括：实现状态校验机制，检测异常状态；提供状态回滚功能，从Git历史恢复；定期备份状态文件。

第三是性能风险，轮询机制可能对Git服务器造成压力。应对措施包括：采用30秒初始间隔和指数退避；支持Webhook作为备选方案；实现变更压缩，减少不必要的检测。

### 7.2 进度风险

开发进度可能受到需求变更、技术难题和测试问题的影响。应对措施包括：采用敏捷开发方法，每两天进行进度评审；预留缓冲时间应对意外情况；优先实现核心功能，非核心功能可以延后。

## 8. 签署确认

### 开发确认

- **签署人**：Agent 2（开发）
- **签署日期**：2026-01-31
- **确认状态**：✓ 已确认

### 产品经理确认

- **签署人**：_________________  日期：_____________
