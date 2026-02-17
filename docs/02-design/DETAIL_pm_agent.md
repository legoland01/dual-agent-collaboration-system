# 详细设计说明书：PM-Agent v1.0.0

**版本**: v1
**创建日期**: 2026-02-16
**作者**: Agent 3 (PM Agent产品经理)
**关联需求**: requirements_pm_agent_v1.0.0_DRAFT.md
**关联概要**: OUTLINE_pm_agent.md
**版本号**: v1.0.0
**状态**: DRAFT

---

## 1. 项目结构

```
pm_agent/
├── frontend/                    # Vue.js前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── HomeView.vue       # F-012 处理结果显示
│   │   │   ├── ProjectsView.vue   # F-004/F-005 项目管理
│   │   │   ├── CustomersView.vue  # F-003 客户管理
│   │   │   ├── DashboardView.vue # F-007 进度总览
│   │   │   ├── IssuesView.vue    # F-008~F-011 问题跟踪
│   │   │   └── SettingsView.vue  # 系统设置
│   │   ├── components/         # 通用组件
│   │   ├── router/             # 路由配置
│   │   ├── api/                # API调用
│   │   └── store/              # 状态管理
│   └── package.json
│
├── backend/                     # FastAPI后端
│   ├── main.py                 # 应用入口
│   ├── api/                    # API路由
│   │   ├── routes/
│   │   │   ├── upload.py       # F-001 文件上传
│   │   │   ├── input.py        # F-001 文本输入
│   │   │   ├── customers.py    # F-003 客户CRUD
│   │   │   ├── projects.py    # F-004/F-005 项目管理
│   │   │   ├── dashboard.py   # F-007 进度数据
│   │   │   ├── issues.py      # F-008~F-011 问题管理
│   │   │   └── sync.py        # F-006 oc-collab同步
│   ├── services/               # 业务逻辑
│   │   ├── input_handler.py    # F-001/F-002 输入处理
│   │   ├── customer_service.py # F-003 客户识别
│   │   ├── project_service.py  # F-004/F-005 项目匹配/路由
│   │   ├── classifier_service.py # F-008 问题分类
│   │   ├── bug_generator_service.py  # F-009 BUG生成
│   │   ├── proposal_generator_service.py # F-010 Proposal生成
│   │   └── feedback_service.py  # F-011 动态反馈
│   ├── integrations/
│   │   └── dossierai_client.py # F-001 dossierai整合
│   ├── models/
│   │   └── database.py         # SQLite数据模型
│   └── requirements.txt
│
└── config/
    └── settings.yaml           # 配置文件
```

---

## 2. 功能模块映射表

### 2.1 需求功能 → 技术模块映射

| 需求ID | 功能名称 | 技术模块 | 文件位置 | 说明 |
|--------|----------|----------|----------|------|
| F-001 | 多模态输入 | InputHandler | services/input_handler.py | 调用dossierai处理 |
| F-001 | 多模态输入 | DossierAIClient | integrations/dossierai_client.py | API客户端 |
| F-002 | 统一输入处理 | InputHandler | services/input_handler.py | 统一入口 |
| F-003 | 客户识别 | CustomerService | services/customer_service.py | 关键词匹配 |
| F-003 | 客户识别 | customers视图 | frontend/views/CustomersView.vue | 前端展示 |
| F-004 | 项目匹配 | ProjectService | services/project_service.py | 项目匹配 |
| F-005 | 自动路由 | ProjectService.route | services/project_service.py | Git路由 |
| F-006 | oc-collab整合 | GitService | services/git_service.py | Git操作 |
| F-007 | 开发文档汇总 | GitService.fetch | services/git_service.py | 拉取文档 |
| F-008 | 问题分类 | ClassifierService | services/classifier_service.py | LLM分类 |
| F-009 | BUG报告生成 | BugGeneratorService | services/bug_generator_service.py | 模板生成 |
| F-010 | Proposal生成 | ProposalGeneratorService | services/proposal_generator_service.py | 模板生成 |
| F-011 | 动态反馈 | FeedbackService | services/feedback_service.py | 状态监控 |
| F-012 | 处理结果显示 | HomeView | frontend/views/HomeView.vue | 结果列表 |

### 2.2 API路由映射

| API路径 | 方法 | 对应功能 | 负责人 |
|---------|------|----------|--------|
| /api/upload | POST | F-001 | InputHandler |
| /api/input/text | POST | F-001 | InputHandler |
| /api/customers | GET/POST | F-003 | CustomerService |
| /api/projects | GET/POST | F-004/F-005 | ProjectService |
| /api/issues | GET | F-008~F-011 | 各Service |
| /api/sync/oc-collab | POST | F-006 | GitService |
| /api/dashboard | GET | F-007 | DashboardService |

---

## 3. 核心模块详细设计

```
pm_agent/
├── frontend/                    # Vue.js前端
│   ├── src/
│   │   ├── views/              # 页面组件
│   │   │   ├── HomeView.vue
│   │   │   ├── ProjectsView.vue
│   │   │   ├── CustomersView.vue
│   │   │   ├── DashboardView.vue
│   │   │   ├── IssuesView.vue
│   │   │   └── SettingsView.vue
│   │   ├── components/         # 通用组件
│   │   ├── router/             # 路由配置
│   │   ├── api/                # API调用
│   │   └── store/              # 状态管理
│   └── package.json
│
├── backend/                     # FastAPI后端
│   ├── main.py                 # 应用入口
│   ├── api/                    # API路由
│   │   ├── routes/
│   │   │   ├── upload.py
│   │   │   ├── customers.py
│   │   │   ├── projects.py
│   │   │   ├── dashboard.py
│   │   │   ├── sync.py
│   │   │   └── issues.py
│   ├── services/               # 业务逻辑
│   │   ├── input_handler.py
│   │   ├── customer_service.py
│   │   ├── project_service.py
│   │   ├── git_service.py
│   │   ├── llm_service.py
│   │   ├── classifier_service.py      # 新增：问题分类
│   │   ├── bug_generator_service.py   # 新增：BUG报告生成
│   │   ├── proposal_generator_service.py  # 新增：Proposal生成
│   │   └── feedback_service.py        # 新增：动态状态反馈
│   ├── models/                 # 数据模型
│   │   └── database.py
│   ├── integrations/           # 外部集成
│   │   └── dossierai_client.py  # 卷宗系统dossierai集成
│   └── requirements.txt
│
└── config/                     # 配置文件
    └── settings.yaml
```

---

## 2. 核心模块详细设计

### 2.1 输入处理模块

#### 2.1.1 DossierAI客户端（整合卷宗系统）

```python
# backend/integrations/dossierai_client.py

import httpx
from typing import Optional, Dict, Any

class DossierAIClient:
    """卷宗系统dossierai服务客户端"""
    
    def __init__(self, base_url: str = "http://localhost:4312/api/v1"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def parse_document(self, file_path: str) -> Dict[str, Any]:
        """
        文档解析/OCR
        API: POST /document/parse
        支持：PDF、图片、文档等
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = await self.client.post(
                f"{self.base_url}/document/parse",
                files=files
            )
        return response.json()
    
    async def recognize_intent(self, text: str) -> Dict[str, Any]:
        """
        意图识别
        API: POST /intent/recognize
        识别：BUG vs 功能需求
        """
        response = await self.client.post(
            f"{self.base_url}/intent/recognize",
            json={"text": text}
        )
        return response.json()
    
    async def chat(self, message: str, context: str = None) -> str:
        """
        AI聊天
        API: POST /message/chat
        用于复杂内容的理解
        """
        payload = {"message": message}
        if context:
            payload["context"] = context
        
        response = await self.client.post(
            f"{self.base_url}/message/chat",
            json=payload
        )
        return response.json().get("response", "")
    
    async def health_check(self) -> bool:
        """检查dossierai服务是否可用"""
        try:
            response = await self.client.get(f"{self.base_url}/health")
            return response.status_code == 200
        except:
            return False
    
    async def close(self):
        await self.client.aclose()
```

#### 2.1.2 InputHandler

```python
# backend/services/input_handler.py

from pathlib import Path
from typing import Optional
from integrations.dossierai_client import DossierAIClient

class InputHandler:
    """统一输入处理器 - 整合dossierai服务"""
    
    IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm'}
    DOC_FORMATS = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    DATA_FORMATS = {'.json', '.csv', '.xlsx', '.log'}
    
    def __init__(self, dossierai_client: DossierAIClient):
        self.dossierai = dossierai_client
    
    def detect_type(self, file_path: str) -> str:
        """检测输入类型"""
        ext = Path(file_path).suffix.lower()
        
        if ext in self.IMAGE_FORMATS:
            return 'image'
        elif ext in self.AUDIO_FORMATS:
            return 'audio'
        elif ext in self.DOC_FORMATS:
            return 'document'
        elif ext in self.DATA_FORMATS:
            return 'data'
        else:
            return 'unknown'
    
    async def process(self, file_path: str, question: str = None) -> dict:
        """统一处理入口 - 调用dossierai"""
        input_type = self.detect_type(file_path)
        
        handlers = {
            'image': self._handle_image,
            'audio': self._handle_audio,
            'document': self._handle_document,
            'data': self._handle_data,
        }
        
        handler = handlers.get(input_type, self._handle_unknown)
        return await handler(file_path, question)
    
    async def _handle_image(self, file_path: str, question: str = None) -> dict:
        """处理图片 - 调用dossierai OCR"""
        # 调用dossierai文档解析API
        result = await self.dossierai.parse_document(file_path)
        
        # 提取文字后，如果有问题可以使用chat理解
        extracted_text = result.get('text', '')
        
        if question:
            understanding = await self.dossierai.chat(question, extracted_text)
            content = understanding
        else:
            content = extracted_text
        
        return {
            'type': 'image',
            'file': file_path,
            'content': content,
            'raw_result': result,
            'entities': await self._extract_entities(content)
        }
    
    async def _handle_audio(self, file_path: str, question: str = None) -> dict:
        """处理音频 - 调用dossierai转录"""
        # dossierai会处理音频转录
        result = await self.dossierai.parse_document(file_path)
        
        transcript = result.get('transcript', '') or result.get('text', '')
        
        if question:
            content = await self.dossierai.chat(question, transcript)
        else:
            content = transcript
        
        return {
            'type': 'audio',
            'file': file_path,
            'transcript': transcript,
            'content': content,
            'raw_result': result,
            'entities': await self._extract_entities(content)
        }
    
    async def _handle_document(self, file_path: str, question: str = None) -> dict:
        """处理文档 - 调用dossierai解析"""
        result = await self.dossierai.parse_document(file_path)
        
        text = result.get('text', '')
        
        if question:
            content = await self.dossierai.chat(question, text)
        else:
            content = text[:2000]  # 截取前2000字
        
        return {
            'type': 'document',
            'file': file_path,
            'content': content,
            'raw_result': result,
            'entities': await self._extract_entities(content)
        }
    
    async def _handle_data(self, file_path: str, question: str = None) -> dict:
        """处理数据文件"""
        # 解析数据文件
        data = self._parse_data(file_path)
        
        # 可以用LLM分析数据
        if question:
            content = await self.dossierai.chat(question, str(data))
        else:
            content = str(data)[:1000]
        
        return {
            'type': 'data',
            'file': file_path,
            'content': content,
            'data': data,
            'entities': await self._extract_entities(content)
        }
    
    async def _handle_unknown(self, file_path: str, question: str = None) -> dict:
        return {
            'type': 'unknown',
            'file': file_path,
            'error': f'不支持的文件类型'
        }
    
    async def _extract_entities(self, text: str) -> dict:
        """调用dossierai进行意图识别/实体提取"""
        result = await self.dossierai.recognize_intent(text)
        return result
    
    def _parse_data(self, file_path: str) -> dict:
        """解析数据文件"""
        ext = Path(file_path).suffix.lower()
        
        if ext == '.json':
            import json
            return json.loads(Path(file_path).read_text())
        elif ext == '.csv':
            # 解析CSV
            pass
        return {}
```

### 2.7 LLM服务（用于分类器fallback）

```python
# backend/services/llm_service.py

import openai
from typing import Optional, List, Dict

class LLMService:
    """LLM服务封装 - ClassifierService fallback使用"""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        openai.api_key = api_key
        self.model = model
    
    def chat(self, prompt: str, system: str = None) -> str:
        """通用对话"""
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        response = openai.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return response.choices[0].message.content
    
    def analyze_image(self, image_path: str, prompt: str) -> str:
        """分析图片"""
        # 使用GPT-4 Vision
        response = openai.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"file://{image_path}"}}
                ]
            }]
        )
        return response.choices[0].message.content
    
    def transcribe(self, audio_path: str) -> str:
        """音频转录"""
        with open(audio_path, "rb") as f:
            response = openai.audio.transcriptions.create(
                model="whisper-1",
                file=f
            )
        return response.text
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """提取实体（客户名、项目名等）"""
        prompt = f"""从以下文本中提取实体：
        
文本：{text}

请提取：
- 客户名（如有）
- 项目名（如有）
- 需求描述
- 优先级

以JSON格式返回：{{"customers": [], "projects": [], "requirements": [], "priority": "P0/P1/P2"}}"""
        
        result = self.chat(prompt)
        import json
        try:
            return json.loads(result)
        except:
            return {"customers": [], "projects": [], "requirements": [], "priority": "P1"}
```

### 2.2 客户识别模块

```python
# backend/services/customer_service.py

from typing import List, Optional
from models.database import Customer

class CustomerService:
    """客户管理服务"""
    
    def __init__(self, db):
        self.db = db
    
    def match(self, content: str) -> Optional[Customer]:
        """从内容中匹配客户"""
        customers = self.db.get_all(Customer)
        
        for customer in customers:
            keywords = customer.keywords.split(',') if customer.keywords else []
            for keyword in keywords:
                if keyword.strip() in content:
                    return customer
        
        return None
    
    def create(self, name: str, keywords: str = None, git_repo: str = None, contact: str = None) -> Customer:
        """创建客户"""
        customer = Customer(
            name=name,
            keywords=keywords,
            git_repo=git_repo,
            contact=contact
        )
        self.db.save(customer)
        return customer
    
    def update(self, customer_id: int, **kwargs) -> Customer:
        """更新客户"""
        customer = self.db.get(Customer, customer_id)
        for key, value in kwargs.items():
            setattr(customer, key, value)
        self.db.save(customer)
        return customer
    
    def delete(self, customer_id: int):
        """删除客户"""
        self.db.delete(Customer, customer_id)
    
    def list_all(self) -> List[Customer]:
        """列出所有客户"""
        return self.db.get_all(Customer)
```

### 2.3 项目管理模块

```python
# backend/services/project_service.py

from typing import List, Optional
from models.database import Project

class ProjectService:
    """项目管理服务"""
    
    def __init__(self, db):
        self.db = db
    
    def match(self, content: str, customer_id: int = None) -> Optional[Project]:
        """从内容中匹配项目"""
        query = self.db.query(Project)
        if customer_id:
            query = query.filter(Project.customer_id == customer_id)
        
        projects = query.all()
        
        for project in projects:
            keywords = project.keywords.split(',') if project.keywords else []
            for keyword in keywords:
                if keyword.strip() in content:
                    return project
        
        return None
    
    def create(self, name: str, customer_id: int = None, git_repo: str = None, **kwargs) -> Project:
        """创建项目"""
        project = Project(
            name=name,
            customer_id=customer_id,
            git_repo=git_repo,
            status='planning',
            progress=0,
            **kwargs
        )
        self.db.save(project)
        return project
    
    def route(self, customer: Customer, project: Project, content: dict) -> str:
        """路由到项目资料库"""
        # 构建目标路径
        target_dir = f"{project.git_repo}/materials/{content.get('type', 'general')}"
        
        # 保存内容
        # git add, commit, push
        
        return target_dir
    
    def list_all(self, customer_id: int = None) -> List[Project]:
        """列出所有项目"""
        query = self.db.query(Project)
        if customer_id:
            query = query.filter(Project.customer_id == customer_id)
        return query.all()
```

### 2.4 Git集成模块

```python
# backend/services/git_service.py

import git
from pathlib import Path

class GitService:
    """Git集成服务"""
    
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
    
    def clone(self, repo_url: str, local_path: str):
        """克隆仓库"""
        git.Repo.clone_from(repo_url, local_path)
    
    def pull(self, local_path: str):
        """拉取更新"""
        repo = git.Repo(local_path)
        repo.remotes.origin.pull()
    
    def create_requirement(self, project_path: str, requirement: dict):
        """创建oc-collab需求"""
        req_path = Path(project_path) / "docs" / "01-requirements"
        req_path.mkdir(parents=True, exist_ok=True)
        
        # 生成需求文件名
        filename = f"REQ-{requirement.get('id', '001')}.md"
        
        # 写入需求文档
        content = self._format_requirement(requirement)
        (req_path / filename).write_text(content, encoding='utf-8')
        
        # Git提交
        repo = git.Repo(project_path)
        repo.index.add([str(req_path / filename)])
        repo.index.commit(f"Add requirement: {filename}")
        repo.remotes.origin.push()
    
    def create_todo(self, project_path: str, todo: dict):
        """创建oc-collab TODO"""
        todo_path = Path(project_path) / "state" / "agent_adhoc_todos.yaml"
        
        # 读取现有TODO
        import yaml
        todos = []
        if todo_path.exists():
            todos = yaml.safe_load(todo_path.read_text(encoding='utf-8')) or []
        
        # 添加新TODO
        todos.append({
            'id': todo.get('id'),
            'content': todo.get('content'),
            'priority': todo.get('priority', 'medium'),
            'status': 'pending',
            'agent_id': todo.get('agent_id', 2),
            'created_at': todo.get('created_at')
        })
        
        # 写入
        todo_path.write_text(yaml.dump(todos), encoding='utf-8')
        
        # Git提交
        repo = git.Repo(project_path)
        repo.index.add([str(todo_path)])
        repo.index.commit(f"Add TODO: {todo.get('id')}")
        repo.remotes.origin.push()
    
    def fetch_development_docs(self, project_path: str) -> list:
        """拉取开发文档"""
        docs_path = Path(project_path)
        
        # 扫描文档目录
        documents = []
        for pattern in ["**/*.md", "**/*.pdf"]:
            documents.extend(docs_path.glob(pattern))
        
        return [{"path": str(p), "name": p.name} for p in documents]

### 2.5 数据流设计

#### 2.5.1 整体数据流

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              外部系统                                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  客户上传   │  │ dossierai   │  │  oc-collab  │                      │
│  │  (文件/文本) │  │  (OCR/转录) │  │  (需求同步) │                      │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                      │
└──────────┼────────────────┼────────────────┼──────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PM-Agent 数据流                                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FastAPI 后端服务                                 │   │
│  │                                                                      │   │
│  │  ┌─────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐   │   │
│  │  │ Input   │───▶│Classifier│───▶│ Generator │───▶│GitService│   │   │
│  │  │Handler  │    │Service   │    │Service   │    │          │   │   │
│  │  └────┬────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘   │   │
│  │       │              │               │               │           │   │
│  │       ▼              ▼               ▼               ▼           │   │
│  │  ┌─────────────────────────────────────────────────────────┐   │   │
│  │  │              SQLite 数据库                               │   │   │
│  │  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │   │
│  │  │  │ customers │  │ projects  │  │ processing│            │   │   │
│  │  │  │   表     │  │   表     │  │  logs表   │            │   │   │
│  │  │  └──────────┘  └──────────┘  └──────────┘            │   │   │
│  │  └─────────────────────────────────────────────────────────┘   │   │
│  │                                                                      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
           │                │                │
           ▼                ▼                ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           输出与同步                                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                      │
│  │  前端展示   │  │ Git仓库    │  │ 客户通知   │                      │
│  │  (处理结果) │  │ (需求文档) │  │ (状态更新) │                      │
│  └─────────────┘  └─────────────┘  └─────────────┘                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### 2.5.2 数据存储位置

| 数据类型 | 存储位置 | 说明 |
|----------|----------|------|
| 客户信息 | `sqlite/customers` 表 | 客户ID、名称、关键词 |
| 项目信息 | `sqlite/projects` 表 | 项目ID、名称、客户ID |
| 处理日志 | `sqlite/processing_logs` 表 | 文件、类型、状态、结果 |
| BUG报告 | `git/{project}/docs/00-memos/` | oc-collab格式BUG |
| Proposal | `git/{project}/docs/04-proposals/` | oc-collab格式需求 |
| TODO | `git/{project}/state/agent_adhoc_todos.yaml` | oc-collab TODO |

#### 2.5.3 状态同步路径

| 场景 | 同步方向 | 触发条件 |
|------|----------|----------|
| 客户材料输入 | 前端→后端→DB | 文件上传完成 |
| 问题分类 | DB→dossierai→DB | 预处理完成 |
| 生成BUG | DB→Git | 分类为BUG |
| 生成Proposal | DB→Git | 分类为需求 |
| 创建TODO | Git→oc-collab | 文档生成完成 |
| 状态反馈 | oc-collab→Git→PM-Agent→客户 | Git状态变更 |

#### 2.5.4 风险点与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| dossierai服务不可用 | 预处理失败 | 添加本地fallback（直接存文件） |
| Git权限问题 | 同步失败 | 添加配置向导，权限检查 |
| 分类不准确 | 误导性问题归属 | 提供人工确认入口 |

### 2.6 问题自动分类模块

```python
# backend/services/classifier_service.py

from typing import Literal
from enum import Enum

class IssueType(Enum):
    BUG = "bug"
    FEATURE_REQUEST = "feature_request"
    OTHER = "other"

class ClassifierService:
    """问题自动分类服务"""
    
    def __init__(self, llm_service: LLMService):
        self.llm = llm_service
    
    def classify(self, content: str) -> tuple[IssueType, dict]:
        """自动分类问题类型"""
        prompt = f"""分析以下内容，判断是BUG报告还是功能需求：

内容：{content}

请返回JSON格式：
{{
    "type": "bug" 或 "feature_request" 或 "other",
    "confidence": 0.0-1.0,
    "reason": "判断理由",
    "severity": "P0/P1/P2/P3" (如果是BUG),
    "priority": "高/中/低" (如果是需求)
}}"""
        
        result = self.llm.chat(prompt)
        import json
        try:
            data = json.loads(result)
            issue_type = IssueType(data['type'])
            return issue_type, data
        except:
            return IssueType.OTHER, {"confidence": 0.0}
    
    def extract_bug_info(self, content: str) -> dict:
        """提取BUG关键信息"""
        prompt = f"""从以下BUG报告中提取关键信息：

内容：{content}

请返回JSON格式：
{{
    "title": "BUG标题",
    "description": "问题描述",
    "steps_to_reproduce": ["步骤1", "步骤2"],
    "expected_behavior": "期望行为",
    "actual_behavior": "实际行为",
    "environment": "环境信息",
    "severity": "P0/P1/P2/P3"
}}"""
        
        result = self.llm.chat(prompt)
        import json
        return json.loads(result)
    
    def extract_requirement_info(self, content: str) -> dict:
        """提取需求关键信息"""
        prompt = f"""从以下需求描述中提取关键信息：

内容：{content}

请返回JSON格式：
{{
    "title": "需求标题",
    "background": "背景",
    "user_scenario": "用户场景",
    "expected_behavior": "期望行为",
    "priority": "高/中/低"
}}"""
        
        result = self.llm.chat(prompt)
        import json
        return json.loads(result)
```

### 2.6 自动生成BUG报告模块

```python
# backend/services/bug_generator_service.py

from datetime import datetime

class BugGeneratorService:
    """自动生成BUG报告服务"""
    
    def __init__(self, git_service: GitService):
        self.git = git_service
    
    def generate(self, project_id: int, bug_info: dict) -> str:
        """生成BUG报告"""
        bug_id = self._generate_bug_id()
        
        content = f"""# Bug报告: {bug_info.get('title', 'BUG')}

**ID**: {bug_id}
**优先级**: {bug_info.get('severity', 'P2')}
**状态**: OPEN
**类型**: 功能缺陷
**创建日期**: {datetime.now().isoformat()}
**发现人**: PM-Agent (自动生成)

---

## 1. Bug描述

### 1.1 问题陈述

{bug_info.get('description', '')}

### 1.2 影响范围

| 命令/功能 | 预期行为 | 实际行为 | 影响 |
|----------|----------|----------|------|
| - | - | - | - |

---

## 2. 重现步骤

### 2.1 步骤1

{bug_info.get('steps_to_reproduce', ['N/A'])}

---

## 3. 根本原因

### 3.1 代码分析

待分析

---

## 4. 解决方案

### 4.1 建议方案

待编写

---

## 5. 验收标准

- [ ] 验收项1

---

## 6. 修复记录

| 日期 | 操作 | 负责人 | 备注 |
|------|------|--------|------|
| {datetime.now().isoformat()} | 创建 | PM-Agent | 自动生成 |

---

## 7. 验证结果

**验证人**:
**验证日期**:
**验证结果**: ✅ 通过 / ❌ 失败
"""
        
        # 保存到项目BUG目录
        self.git.save_bug_report(project_id, bug_id, content)
        
        return bug_id
    
    def _generate_bug_id(self) -> str:
        """生成BUG ID"""
        return f"BUG-{datetime.now().strftime('%Y%m%d')}-{001}"
```

### 2.7 自动生成Proposal模块

```python
# backend/services/proposal_generator_service.py

class ProposalGeneratorService:
    """自动生成Proposal服务"""
    
    def __init__(self, git_service: GitService):
        self.git = git_service
    
    def generate(self, project_id: int, req_info: dict) -> str:
        """生成功能Proposal"""
        proposal_id = self._generate_proposal_id()
        
        content = f"""# {req_info.get('title', '功能需求')}

**ID**: {proposal_id}
**提案人**: PM-Agent (自动生成)
**日期**: {datetime.now().isoformat()}
**目标版本**: v1.0.0
**状态**: DRAFT

---

## 1. 问题背景

{req_info.get('background', '')}

## 2. 解决方案

待编写

## 3. 用户场景

{req_info.get('user_scenario', '')}

## 4. 优先级

{req_info.get('priority', '中')}

## 5. 依赖

无

## 6. 验收标准

- [ ] 验收项1

## 7. 估算工时

待评估

## 8. 签署确认

| 角色 | 签署人 | 状态 | 日期 |
|------|--------|------|------|
"""
        
        # 保存到项目Proposal目录
        self.git.save_proposal(project_id, proposal_id, content)
        
        return proposal_id
    
    def _generate_proposal_id(self) -> str:
        """生成Proposal ID"""
        return f"PROPOSAL-{datetime.now().strftime('%Y-%m')}-{001}"
```

### 2.8 动态状态反馈模块

```python
# backend/services/feedback_service.py

import time
from threading import Thread

class FeedbackService:
    """动态状态反馈服务"""
    
    def __init__(self, git_service: GitService, issue_service):
        self.git = git_service
        self.issue_service = issue_service
        self.running = False
    
    def start_monitoring(self, project_id: int, interval: int = 60):
        """启动状态监控"""
        self.running = True
        thread = Thread(target=self._monitor_loop, args=(project_id, interval))
        thread.daemon = True
        thread.start()
    
    def stop_monitoring(self):
        """停止监控"""
        self.running = False
    
    def _monitor_loop(self, project_id: int, interval: int):
        """监控循环"""
        while self.running:
            try:
                self._check_and_update_status(project_id)
            except Exception as e:
                print(f"监控出错: {e}")
            time.sleep(interval)
    
    def _check_and_update_status(self, project_id: int):
        """检查并更新状态"""
        # 1. 拉取最新代码
        self.git.pull(project_id)
        
        # 2. 检查BUG状态
        open_bugs = self.issue_service.get_open_bugs(project_id)
        for bug in open_bugs:
            if self._is_bug_fixed(bug):
                self.issue_service.update_status(bug['id'], 'RESOLVED')
                self._notify_customer(bug, 'BUG已修复')
        
        # 3. 检查需求状态
        open_requirements = self.issue_service.get_open_requirements(project_id)
        for req in open_requirements:
            if self._is_requirement_completed(req):
                self.issue_service.update_status(req['id'], 'COMPLETED')
                self._notify_customer(req, '功能已完成')
    
    def _is_bug_fixed(self, bug: dict) -> bool:
        """检查BUG是否已修复"""
        # 检查对应commit message
        commits = self.git.get_recent_commits()
        return any(f"fix {bug['id']}" in c.message.lower() for c in commits)
    
    def _is_requirement_completed(self, req: dict) -> bool:
        """检查需求是否已完成"""
        # 检查需求文档状态
        return self.git.check_requirement_completed(req['id'])
    
    def _notify_customer(self, issue: dict, message: str):
        """通知客户"""
        # 可以通过邮件、Webhook等方式通知
        print(f"通知客户: {issue['customer']} - {message}")


---

## 3. API详细设计

### 3.1 文件上传API

```python
# backend/api/routes/upload.py

from fastapi import APIRouter, UploadFile, File, Form
from typing import Optional

router = APIRouter()

@router.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...),
    question: Optional[str] = Form(None)
):
    """上传文件处理"""
    # 1. 保存上传的文件
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 2. 调用InputHandler处理
    handler = get_input_handler()
    result = handler.process(temp_path, question)
    
    # 3. 匹配客户和项目
    customer = customer_service.match(result['content'])
    project = project_service.match(result['content'], customer.id if customer else None)
    
    # 4. 路由到项目
    if project:
        route_path = project_service.route(customer, project, result)
        result['route'] = route_path
    
    # 5. 保存处理日志
    log_service.save(result)
    
    return {
        "success": True,
        "data": result,
        "customer": customer.name if customer else None,
        "project": project.name if project else None
    }

@router.post("/api/input/text")
async def process_text(text: str, question: Optional[str] = None):
    """文本输入处理"""
    # 类似上传处理，但不保存文件
    result = handler.process_text(text, question)
    
    # 匹配客户和项目
    customer = customer_service.match(result['content'])
    project = project_service.match(result['content'], customer.id if customer else None)
    
    return {
        "success": True,
        "data": result,
        "customer": customer.name if customer else None,
        "project": project.name if project else None
    }
```

### 3.2 客户管理API

```python
# backend/api/routes/customers.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class CustomerCreate(BaseModel):
    name: str
    keywords: str = None
    git_repo: str = None
    contact: str = None

@router.get("/api/customers")
def list_customers():
    """获取客户列表"""
    return customer_service.list_all()

@router.post("/api/customers")
def create_customer(data: CustomerCreate):
    """创建客户"""
    return customer_service.create(**data.dict())

@router.put("/api/customers/{customer_id}")
def update_customer(customer_id: int, data: CustomerCreate):
    """更新客户"""
    return customer_service.update(customer_id, **data.dict())

@router.delete("/api/customers/{customer_id}")
def delete_customer(customer_id: int):
    """删除客户"""
    customer_service.delete(customer_id)
    return {"success": True}
```

### 3.3 项目管理API

```python
# backend/api/routes/projects.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ProjectCreate(BaseModel):
    name: str
    customer_id: int = None
    keywords: str = None
    git_repo: str = None
    oc_collab_enabled: bool = False

@router.get("/api/projects")
def list_projects(customer_id: int = None):
    """获取项目列表"""
    return project_service.list_all(customer_id)

@router.get("/api/projects/{project_id}")
def get_project(project_id: int):
    """获取项目详情"""
    project = project_service.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/api/projects")
def create_project(data: ProjectCreate):
    """创建项目"""
    return project_service.create(**data.dict())
```

### 3.4 同步API

```python
# backend/api/routes/sync.py

from fastapi import APIRouter

router = APIRouter()

@router.post("/api/sync/oc-collab")
def sync_to_oc_collab(project_id: int):
    """同步到oc-collab项目"""
    # 1. 获取项目信息
    project = project_service.get(project_id)
    
    # 2. 从处理日志中获取待处理需求
    pending = log_service.get_pending_for_project(project_id)
    
    # 3. 写入oc-collab仓库
    for item in pending:
        git_service.create_requirement(project.git_repo, item)
        git_service.create_todo(project.git_repo, item['todo'])
        
        # 更新状态
        log_service.mark_synced(item['id'])
    
    return {"success": True, "synced_count": len(pending)}

@router.get("/api/sync/status/{project_id}")
def get_sync_status(project_id: int):
    """获取同步状态"""
    return log_service.get_sync_status(project_id)
```

---

## 4. 数据库设计

### 4.1 数据库Schema

```sql
-- PM-Agent SQLite 数据库
-- 文件: data/pm_agent.db

-- 客户表
CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    keywords TEXT,
    git_repo TEXT,
    contact TEXT,
    status TEXT DEFAULT 'active' CHECK(status IN ('active', 'inactive')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 项目表
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER,
    name TEXT NOT NULL,
    keywords TEXT,
    status TEXT DEFAULT 'planning' CHECK(status IN ('planning', 'developing', 'testing', 'online', 'archived')),
    progress INTEGER DEFAULT 0 CHECK(progress >= 0 AND progress <= 100),
    git_repo TEXT,
    oc_collab_enabled BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
);

-- 处理日志表
CREATE TABLE processing_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    input_type TEXT NOT NULL CHECK(input_type IN ('image', 'audio', 'document', 'data', 'text')),
    file_path TEXT,
    content TEXT,
    extracted_text TEXT,
    dossierai_response TEXT,
    issue_type TEXT CHECK(issue_type IN ('bug', 'feature_request', 'other', 'unknown')),
    issue_id TEXT,
    customer_id INTEGER,
    project_id INTEGER,
    result TEXT CHECK(result IN ('pending', 'processing', 'completed', 'failed', 'need_confirm')),
    error_message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE SET NULL
);

-- 操作日志表（新增）
CREATE TABLE operation_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,
    target_type TEXT,
    target_id TEXT,
    details TEXT,
    operator TEXT DEFAULT 'system',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- BUG报告表
CREATE TABLE bugs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bug_id TEXT NOT NULL UNIQUE,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    severity TEXT CHECK(severity IN ('P0', 'P1', 'P2', 'P3')),
    status TEXT DEFAULT 'open' CHECK(status IN ('open', 'in_progress', 'resolved', 'closed', 'rejected')),
    steps_to_reproduce TEXT,
    expected_behavior TEXT,
    actual_behavior TEXT,
    environment TEXT,
    assigned_to TEXT,
    oc_git_commit_hash TEXT,
    created_by TEXT DEFAULT 'PM-Agent',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Proposal/需求表
CREATE TABLE proposals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    proposal_id TEXT NOT NULL UNIQUE,
    project_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    background TEXT,
    user_scenario TEXT,
    expected_behavior TEXT,
    priority TEXT CHECK(priority IN ('high', 'medium', 'low')),
    status TEXT DEFAULT 'draft' CHECK(status IN ('draft', 'review', 'approved', 'rejected', 'implemented')),
    estimated_hours REAL,
    oc_git_commit_hash TEXT,
    created_by TEXT DEFAULT 'PM-Agent',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    implemented_at DATETIME,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- 系统配置表
CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT NOT NULL UNIQUE,
    value TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 4.2 索引设计

```sql
-- 客户索引
CREATE INDEX idx_customers_name ON customers(name);
CREATE INDEX idx_customers_status ON customers(status);

-- 项目索引
CREATE INDEX idx_projects_customer_id ON projects(customer_id);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_name ON projects(name);

-- 处理日志索引
CREATE INDEX idx_processing_logs_customer_id ON processing_logs(customer_id);
CREATE INDEX idx_processing_logs_project_id ON processing_logs(project_id);
CREATE INDEX idx_processing_logs_issue_type ON processing_logs(issue_type);
CREATE INDEX idx_processing_logs_result ON processing_logs(result);
CREATE INDEX idx_processing_logs_created_at ON processing_logs(created_at);

-- BUG索引
CREATE INDEX idx_bugs_project_id ON bugs(project_id);
CREATE INDEX idx_bugs_bug_id ON bugs(bug_id);
CREATE INDEX idx_bugs_severity ON bugs(severity);
CREATE INDEX idx_bugs_status ON bugs(status);

-- Proposal索引
CREATE INDEX idx_proposals_project_id ON proposals(project_id);
CREATE INDEX idx_proposals_proposal_id ON proposals(proposal_id);
CREATE INDEX idx_proposals_priority ON proposals(priority);
CREATE INDEX idx_proposals_status ON proposals(status);

-- 操作日志索引（新增）
CREATE INDEX idx_operation_logs_type ON operation_logs(operation_type);
CREATE INDEX idx_operation_logs_target ON operation_logs(target_type, target_id);
CREATE INDEX idx_operation_logs_created_at ON operation_logs(created_at);
```

### 4.3 ORM模型（SQLAlchemy）

```python
# backend/models/database.py

from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    keywords = Column(Text)
    git_repo = Column(String(500))
    contact = Column(String(255))
    status = Column(String(20), default='active')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    projects = relationship("Project", back_populates="customer")
    processing_logs = relationship("ProcessingLog", back_populates="customer")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='SET NULL'))
    name = Column(String(255), nullable=False)
    keywords = Column(Text)
    status = Column(String(20), default='planning')
    progress = Column(Integer, default=0)
    git_repo = Column(String(500))
    oc_collab_enabled = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    customer = relationship("Customer", back_populates="projects")
    processing_logs = relationship("ProcessingLog", back_populates="project")
    bugs = relationship("Bug", back_populates="project")
    proposals = relationship("Proposal", back_populates="project")

class ProcessingLog(Base):
    __tablename__ = 'processing_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    input_type = Column(String(20), nullable=False)
    file_path = Column(String(500))
    content = Column(Text)
    extracted_text = Column(Text)
    issue_type = Column(String(20))
    issue_id = Column(String(50))
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='SET NULL'))
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='SET NULL'))
    result = Column(String(20), default='pending')
    error_message = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    customer = relationship("Customer", back_populates="processing_logs")
    project = relationship("Project", back_populates="processing_logs")

class Bug(Base):
    __tablename__ = 'bugs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    bug_id = Column(String(50), nullable=False, unique=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(5))
    status = Column(String(20), default='open')
    steps_to_reproduce = Column(Text)
    expected_behavior = Column(Text)
    actual_behavior = Column(Text)
    environment = Column(Text)
    assigned_to = Column(String(100))
    created_by = Column(String(50), default='PM-Agent')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    resolved_at = Column(DateTime)
    
    project = relationship("Project", back_populates="bugs")

class Proposal(Base):
    __tablename__ = 'proposals'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    proposal_id = Column(String(50), nullable=False, unique=True)
    project_id = Column(Integer, ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    title = Column(String(255), nullable=False)
    background = Column(Text)
    user_scenario = Column(Text)
    expected_behavior = Column(Text)
    priority = Column(String(10))
    status = Column(String(20), default='draft')
    estimated_hours = Column(Float)
    created_by = Column(String(50), default='PM-Agent')
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    implemented_at = Column(DateTime)
    
    project = relationship("Project", back_populates="proposals")

class Setting(Base):
    __tablename__ = 'settings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(Text)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数据库初始化
DATABASE_URL = "sqlite:///./data/pm_agent.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.4 数据关系图

```
┌─────────────┐       ┌─────────────┐       ┌──────────────────┐
│  customers  │       │  projects   │       │ processing_logs  │
├─────────────┤       ├─────────────┤       ├──────────────────┤
│ id (PK)     │◄──────│ customer_id │       │ id (PK)          │
│ name        │       │ id (PK)     │◄──────│ customer_id (FK) │
│ keywords    │       │ name        │       │ project_id (FK)  │
│ git_repo    │       │ customer_id │       │ issue_type       │
│ contact     │       │ status      │       │ issue_id         │
│ status      │       │ progress    │       │ result           │
└─────────────┘       └──────┬──────┘       └──────────────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌───────────┐  ┌───────────┐  ┌───────────┐
       │   bugs    │  │ proposals │  │ settings  │
       ├───────────┤  ├───────────┤  ├───────────┤
       │ id (PK)   │  │ id (PK)   │  │ id (PK)   │
       │ bug_id    │  │ proposal_ │  │ key       │
       │ project_id│  │ id        │  │ value     │
       │ title     │  │ title     │  └───────────┘
       │ severity  │  │ priority  │
       │ status   │  │ status    │
       └───────────┘  └───────────┘
```

---

## 5. 前端组件设计

### 4.1 信息输入页

```vue
<!-- frontend/src/views/HomeView.vue -->

<template>
  <div class="home-view">
    <h1>📥 信息输入</h1>
    
    <!-- 文件上传区 -->
    <div 
      class="upload-zone"
      @drop="handleDrop"
      @click="triggerUpload"
    >
      <input 
        type="file" 
        ref="fileInput" 
        multiple 
        @change="handleFileSelect"
        style="display: none"
      />
      <p>拖拽文件到此处，或点击上传</p>
      <p class="hint">支持：图片 / 音频 / 文档 / 日志</p>
    </div>
    
    <!-- 手动输入区 -->
    <div class="text-input">
      <h3>手动输入</h3>
      <textarea 
        v-model="textInput" 
        placeholder="在这里输入项目相关信息..."
        rows="4"
      ></textarea>
      <button @click="submitText">提交</button>
    </div>
    
    <!-- 处理历史 -->
    <div class="history">
      <h3>最近处理</h3>
      <div v-for="item in history" :key="item.id" class="history-item">
        <span class="time">{{ item.time }}</span>
        <span class="customer">{{ item.customer }}</span>
        <span class="type">{{ item.type }}</span>
        <span class="status">{{ item.status }}</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { uploadApi, processTextApi } from '@/api/pm-agent'

const fileInput = ref(null)
const textInput = ref('')
const history = ref([])

const handleFileSelect = async (event) => {
  const files = event.target.files
  for (const file of files) {
    const formData = new FormData()
    formData.append('file', file)
    await uploadApi(formData)
  }
  refreshHistory()
}

const submitText = async () => {
  await processTextApi({ text: textInput.value })
  textInput.value = ''
  refreshHistory()
}

const refreshHistory = async () => {
  // 获取处理历史
}
</script>
```

---

## 5. 部署配置

### 5.1 Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - VITE_API_BASE=http://backend:8000
    
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./config:/app/config
      - ./data:/app/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DATABASE_URL=sqlite:///./data/pm_agent.db
```

---

## 6. 验收标准

| 模块 | 验收标准 |
|------|----------|
| InputHandler | 能正确识别并处理所有支持的文件类型 |
| LLMService | 能正确调用OpenAI API并解析结果 |
| CustomerService | 能正确匹配客户 |
| ProjectService | 能正确匹配项目并路由 |
| GitService | 能正确写入oc-collab格式的文档 |
| API | 所有API按设计实现并可调用 |
| 前端 | 所有页面按UI设计实现 |

---

## 8. 测试策略

### 8.1 单元测试

| 模块 | 测试用例 | 测试目标 |
|------|----------|----------|
| InputHandler | test_detect_type_image | 正确识别图片类型 |
| InputHandler | test_detect_type_audio | 正确识别音频类型 |
| InputHandler | test_detect_type_document | 正确识别文档类型 |
| InputHandler | test_process_image | 调用dossierai处理图片 |
| DossierAIClient | test_parse_document | 文档解析API调用 |
| DossierAIClient | test_recognize_intent | 意图识别API调用 |
| DossierAIClient | test_health_check | 服务健康检查 |
| CustomerService | test_match_customer | 客户关键词匹配 |
| CustomerService | test_create_customer | 创建客户 |
| ProjectService | test_match_project | 项目匹配 |
| ProjectService | test_route | 自动路由功能 |
| ClassifierService | test_classify_bug | 识别BUG类型 |
| ClassifierService | test_classify_requirement | 识别需求类型 |
| BugGeneratorService | test_generate_bug_report | 生成BUG报告 |
| ProposalGeneratorService | test_generate_proposal | 生成Proposal |
| GitService | test_create_requirement | Git写入需求 |
| GitService | test_create_todo | Git写入TODO |
| FeedbackService | test_check_bug_fixed | 检查BUG修复状态 |

### 8.2 E2E测试场景

| 场景 | 测试步骤 | 预期结果 |
|------|----------|----------|
| 文件上传处理流程 | 1.上传图片 → 2.调用dossierai → 3.分类 → 4.生成报告 | 完整流程执行成功 |
| 客户识别流程 | 1.输入文本含客户关键词 → 2.匹配客户 → 3.返回客户信息 | 正确识别客户 |
| 项目匹配流程 | 1.输入文本含项目关键词 → 2.匹配项目 → 3.路由到项目 | 正确匹配和路由 |
| BUG报告生成流程 | 1.识别为BUG → 2.生成报告 → 3.写入Git | 报告生成并存储 |
| oc-collab同步流程 | 1.创建需求 → 2.写入oc-collab仓库 → 3.创建TODO | 同步成功 |

### 8.3 测试技术选型

| 类型 | 工具 | 说明 |
|------|------|------|
| 单元测试 | pytest | Python后端测试 |
| API测试 | FastAPI TestClient | HTTP接口测试 |
| 前端测试 | Vitest | Vue组件测试 |
| E2E测试 | Playwright | 端到端测试 |

### 8.4 测试环境

| 环境 | 用途 | 配置 |
|------|------|------|
| dev | 开发调试 | 本地dossierai |
| test | 单元测试 | Mock dossierai |
| staging | E2E测试 | Docker-compose |

---

## 9. 错误处理

### 9.1 错误类型定义

| 错误码 | 类型 | 说明 |
|--------|------|------|
| E001 | InputError | 不支持的文件类型 |
| E002 | DossierAIError | dossierai服务调用失败 |
| E003 | GitError | Git操作失败 |
| E004 | DatabaseError | 数据库操作失败 |
| E005 | ClassifierError | 分类失败 |

### 9.2 错误处理策略

| 场景 | 处理方式 |
|------|----------|
| dossierai不可用 | 返回原始文件，记录日志 |
| Git权限错误 | 提示配置检查 |
| 分类不准确 | 提供人工确认入口 |
| 网络超时 | 重试3次后返回失败 |

---

## 7. 签署确认

### Agent 3 创建

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 产品负责人 | Agent 3 | 2026-02-16 | ✅ |

### Agent 2 评审

| 角色 | 姓名 | 日期 | 确认 |
|------|------|------|------|
| 开发负责人 | Agent 2 | - | ⏳ |

---

**文档版本**: v1
**创建日期**: 2026-02-16
**修订日期**: 2026-02-16
**状态**: DRAFT
