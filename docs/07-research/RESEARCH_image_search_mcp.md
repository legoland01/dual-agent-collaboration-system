# Research: 多模态输入 + 客户声音整合

**目标**: 探索如何利用图片、录音及各种客户声音增强 oc-collab

**日期**: 2026-02-15
**状态**: 🔬 Exploring

---

## 1. 客户声音来源汇总

### 1.1 沟通记录

| 来源类型 | 格式 | 处理方式 |
|---------|------|---------|
| 微信截图 | 图片 | OCR + LLM 理解 |
| 微信语音 | 音频 | 转录 + 理解 |
| 微信文件 | PDF/文档 | 提取 + 理解 |
| 电话录音 | 音频 | 转录 + 理解 |
| 会议录音 | 音频 | 转录 + 理解 |
| 会议纪要 | Markdown/Word | 直接理解 |

### 1.2 需求文档

| 来源类型 | 格式 | 处理方式 |
|---------|------|---------|
| 客户需求文档 | Word/PDF | 提取文本 |
| 需求访谈记录 | 音频/文字 | 转录/理解 |
| 问卷结果 | Excel/CSV | 数据分析 |
| 客户问题报告 | 文档 | 提取要点 |

### 1.3 反馈与调研

| 来源类型 | 格式 | 处理方式 |
|---------|------|---------|
| 客户调研结论 | 文档 | 理解要点 |
| 客户访谈记录 | 音频/文字 | 转录/理解 |
| 问卷分析报告 | 文档/图表 | 理解结论 |
| 回访记录 | 文字/音频 | 转录/理解 |

### 1.4 系统运行记录

| 来源类型 | 格式 | 处理方式 |
|---------|------|---------|
| 日志文件 | .log/.txt | 日志分析 |
| 问题报告 | 文档/Markdown | 理解问题 |
| 运维报告 | 文档 | 理解状态 |
| 监控数据 | JSON/CSV | 数据分析 |

---

## 2. 输入类型与处理方式

### 2.1 图片类

```
微信截图 → OCR提取文字 → LLM理解
设计稿截图 → LLM理解设计意图
流程图截图 → LLM提取流程步骤
报表截图 → LLM提取数据/趋势
```

### 2.2 音频类

```
微信语音 → 转录 → LLM理解
电话录音 → 转录 → LLM理解
会议录音 → 转录 → LLM总结要点
```

### 2.3 文档类

```
Word → 提取文本 → LLM理解
PDF → 提取文本 → LLM理解
Excel → 提取数据 → LLM分析
Markdown → 直接读取 → LLM理解
```

### 2.4 结构化数据

```
JSON → 解析 → LLM分析
CSV → 解析 → LLM分析
日志 → 解析 → LLM分析错误
```

---

## 3. 统一处理框架

### 3.1 输入类型识别

```python
# src/core/input_handler.py

class InputHandler:
    """统一输入处理器"""
    
    IMAGE_FORMATS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'}
    AUDIO_FORMATS = {'.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm'}
    DOC_FORMATS = {'.pdf', '.docx', '.doc', '.txt', '.md'}
    DATA_FORMATS = {'.json', '.csv', '.xlsx', '.log'}
    
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
```

### 3.2 处理器注册

```python
# src/core/handlers/

class HandlerRegistry:
    """处理器注册表"""
    
    handlers = {
        'image': ImageHandler(),      # 图片处理
        'audio': AudioHandler(),      # 音频处理  
        'document': DocumentHandler(), # 文档处理
        'data': DataHandler(),       # 数据处理
    }
    
    def process(self, file_path: str, question: str = None) -> str:
        """统一处理入口"""
        input_type = self.detect_type(file_path)
        handler = self.handlers.get(input_type)
        
        if not handler:
            return f"不支持的文件类型: {input_type}"
        
        return handler.process(file_path, question)
```

### 3.3 具体处理器

```python
class ImageHandler:
    """图片处理器"""
    
    def process(self, file_path: str, question: str = None) -> str:
        # 1. 读取图片
        image_data = Path(file_path).read_bytes()
        
        # 2. 发送给 LLM
        prompt = question or "描述这张图片的内容"
        return llm.analyze_image(image_data, prompt)


class AudioHandler:
    """音频处理器"""
    
    def process(self, file_path: str, question: str = None) -> str:
        # 1. 读取音频
        audio_data = Path(file_path).read_bytes()
        
        # 2. 转录
        transcript = llm.transcribe(audio_data)
        
        # 3. 如果有问题，基于转录回答
        if question:
            return llm.answer(f"基于以下转录回答问题：{transcript}\n\n问题：{question}")
        
        # 4. 否则总结
        return llm.summarize(transcript)


class DocumentHandler:
    """文档处理器"""
    
    def process(self, file_path: str, question: str = None) -> str:
        # 1. 提取文本
        text = self.extract_text(file_path)
        
        # 2. 发送给 LLM
        if question:
            return llm.answer(f"基于以下文档回答问题：{text}\n\n问题：{question}")
        
        return text[:1000]  # 返回前1000字


class DataHandler:
    """数据处理器"""
    
    def process(self, file_path: str, question: str = None) -> str:
        # 1. 解析数据
        data = self.parse_data(file_path)
        
        # 2. 发送给 LLM 分析
        prompt = question or "分析这些数据"
        return llm.analyze_data(data, prompt)
```

---

## 4. CLI 命令设计

```bash
# 统一入口
oc-collab process <file> "问题可选"
oc-collab process screenshot.png "这是什么问题"
oc-collab process meeting.m4a "提取需求要点"
oc-collab process requirements.docx "总结需求"

# 分类命令
oc-collab vision describe "描述这张图" image.png
oc-collab audio transcribe meeting.m4a
oc-collab audio summarize "总结要点" meeting.m4a
oc-collab doc extract requirements.pdf

# 客户声音专用的
oc-collab customer voice screenshot.png "客户反馈什么问题"
oc-collab customer call call_recording.m4a "客户说了什么"
oc-collab customer meeting meeting.m4a "提取客户需求"

# 系统日志
oc-collab system analyze-logs error.log "分析错误原因"
oc-collab system report运维报告.md "总结系统状态"
```

---

## 5. 典型使用场景

### 场景1: 客户微信反馈

```
客户: [截图] "这个功能不能用"
    ↓
处理: 微信截图 → OCR提取文字 + LLM理解
    ↓
结果: "页面显示 '登录失败，用户名或密码错误'，可能原因：..."
```

### 场景2: 客户电话

```
客户: [电话录音] 投诉某功能
    ↓
处理: 录音转录 + LLM提取要点
    ↓
结果: "客户反馈：1. 系统响应慢 2. 导出功能报错 3. 建议增加批量操作"
```

### 场景3: 会议录音

```
会议: [录音] 需求评审会议
    ↓
处理: 转录 + LLM总结
    ↓
结果: "会议结论：
- 需要实现用户管理模块
- 需要支持第三方登录
- 上线时间：Q2"
```

### 场景4: 系统日志

```
日志: [error.log] 服务器报错
    ↓
处理: 解析日志 + LLM分析错误
    ↓
结果: "错误原因：数据库连接池耗尽
建议：增加连接池大小或优化查询"
```

---

## 6. 数据流设计

```
┌─────────────────────────────────────────────────────────────┐
│                     输入来源                                   │
│  微信截图/语音  电话录音  会议录音  需求文档  系统日志       │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   InputHandler                              │
│         (自动识别文件类型)                                  │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────┬───────────┬───────────┬───────────┐
        ▼           ▼           ▼           ▼           │
   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
   │Image    │ │Audio    │ │Document │ │Data     │
   │Handler  │ │Handler  │ │Handler  │ │Handler  │
   └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
        │           │           │           │
        └───────────┴─────┬─────┴───────────┘
                          │
                          ▼
              ┌───────────────────────┐
              │       LLM            │
              │  (理解/分析/总结)    │
              └──────────┬──────────┘
                         │
                         ▼
              ┌───────────────────────┐
              │      输出结果         │
              │  理解/分析/报告/需求  │
              └───────────────────────┘
```

---

## 7. 下一步探索

- [ ] 测试各类型文件处理
- [ ] 完善处理器实现
- [ ] CLI 命令整合

---

**状态**: 🔬 探索中
