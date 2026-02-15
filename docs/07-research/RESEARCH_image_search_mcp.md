# Research: 图片输入 + 联网搜索 MCP 整合

**目标**: 探索如何利用图片输入和联网搜索能力增强 oc-collab

**日期**: 2026-02-15
**状态**: 🔬 Exploring

---

## 1. 新能力概述

### 1.1 图片输入能力

- 模型可以接收图片作为输入
- 可以理解截图、图表、UI 等视觉内容

### 1.2 联网搜索 MCP

- 可以调用外部搜索 API
- 实时获取互联网信息

---

## 2. 整合场景探索

### 2.1 图片输入场景

| 场景 | 应用 |
|------|------|
| UI 测试 | 截图对比，验证 UI 正确性 |
| 错误截图 | 分析错误截图，辅助 Debug |
| 文档截图 | 理解手写/截图文档 |
| 设计稿 | 分析设计稿截图 |

### 2.2 联网搜索场景

| 场景 | 应用 |
|------|------|
| PyPI 包查询 | 搜索依赖包最新版本 |
| GitHub 查询 | 搜索代码示例 |
| 文档查询 | 搜索第三方库文档 |
| 错误搜索 | 搜索错误解决方案 |

---

## 3. 初步整合方案

### 3.1 图片输入

```python
# 示例：截图对比测试

def test_ui_screenshot():
    """测试 UI 截图"""
    # 截图当前界面
    screenshot = capture_screenshot()
    
    # 发送给 LLM 分析
    result = llm.analyze_image(
        screenshot,
        "这个界面是否符合设计稿？"
    )
    
    assert "符合" in result
```

### 3.2 联网搜索

```python
# 示例：自动搜索依赖包版本

def check_dependency_version(package_name: str):
    """检查依赖包最新版本"""
    result = mcp_search(
        f"pypi {package_name} latest version"
    )
    return result["version"]
```

---

## 4. 下一步探索

- [ ] 测试图片输入 API
- [ ] 测试联网搜索 MCP
- [ ] 设计整合方案

---

**状态**: 🔬 探索中
