# Patch发布指南

**版本**: v1.0.0  
**适用阶段**: patch  
**Agent**: Agent 1, Agent 2

---

## SOP结构概览

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 见"1. Patch触发条件"章节 |
| **2. 操作步骤** | 见"2. Patch发布流程"章节 |
| **3. 输出产物** | v2.2.12.1, CHANGELOG.md, Git tag |
| **4. 验收标准** | 见"4. Patch验收标准"章节 |

---

## 1. Patch触发条件

### 1.1 判断是否需要发布Patch

**Patch发布条件**：

| 条件 | 说明 | 是否发布Patch |
|------|------|--------------|
| 影响日常开发 | 阻塞Agent协作 | ✅ 是 |
| 阻塞工作流程 | 无法正常完成TODO | ✅ 是 |
| YAML/数据损坏 | 导致数据丢失或错误 | ✅ 是 |
| 安全漏洞 | 需要立即修复 | ✅ 是 |
| 功能增强 | 新功能需求 | ❌ 否 |
| 体验优化 | 非阻塞性问题 | ❌ 否 |

### 1.2 Patch优先级

| 优先级 | 条件 | 响应时间 |
|--------|------|----------|
| **P0** | 阻塞开发 | 立即修复，24h内发布 |
| **P1** | 影响效率 | 24-48h内发布 |
| **P2** | 小问题 | 下个版本修复 |

### 1.3 版本号格式

```
v{Major}.{Minor}.{Patch}.{Fix}

示例:
- v2.2.12  →  v2.2.12.1 (第一个patch)
- v2.2.12.1 → v2.2.12.2 (第二个patch)
```

### 1.4 版本号自增规则

| 操作 | 自增方式 |
|------|----------|
| 修复第一个Bug | 2.2.12 → 2.2.12.1 |
| 修复第二个Bug（同一版本） | 2.2.12.1 → 2.2.12.2 |
| 新功能 | 2.2.12 → 2.2.13 |
| 不兼容变更 | 2.2.x → 3.0.0 |

---

## 2. Patch发布流程

```
发现Bug
    │
    ▼
判断是否需要Patch？
    │
    ▼
创建Bug报告
    │
    ▼
创建Patch TODO
    │
    ▼
修复Bug
    │
    ▼
Patch验收
    │
    ▼
发布Patch
```

### 2.1 创建Bug报告

```markdown
# BUG报告：问题描述

**BUG编号**: BUG-YYYYMMDD-XXX
**发现日期**: YYYY-MM-DD
**发现者**: Agent X
**优先级**: P0/P1/P2
**状态**: OPEN

---

## 问题描述
[问题描述]

## 复现步骤
1. 步骤1
2. 步骤2

## 影响范围
[影响哪些功能]

## 修复方案
[初步方案]
```

### 2.2 创建Patch TODO

```bash
oc-collab todowrite --content "修复BUG-YYYYMMDD-XXX: 问题标题" --priority P0
```

### 2.3 修复Bug

按照正常开发流程修复Bug：
1. 查看Bug报告
2. 分析根因
3. 实现修复
4. 单元测试

### 2.4 Patch验收标准

| 验收项 | 标准 | 检查方式 |
|--------|------|----------|
| Bug已修复 | 原问题不再存在 | 手动验证 |
| 无回归 | 现有功能正常 | 单元测试 |
| 代码质量 | 无严重警告 | pytest/ruff |
| 文档更新 | CHANGELOG已更新 | grep验证 |

### 2.5 发布Patch

#### 步骤1：更新版本号

```bash
# 编辑 pyproject.toml
[project]
version = "2.2.12.1"  # 更新版本号
```

#### 步骤2：更新CHANGELOG.md

```markdown
## v2.2.12.1 (2026-02-15)

### Fixed
- BUG-20260215-001: TODO编号生成逻辑
- BUG-20260215-002: AutoBugDetector未工作

### Changed
- (无)

### Security
- (无)
```

#### 步骤3：构建包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
python -m build
```

#### 步骤4：PyPI上传

```bash
# 上传到PyPI
twine upload dist/*
```

#### 步骤5：Git推送

```bash
# 提交变更
git add pyproject.toml CHANGELOG.md
git commit -m "fix: patch v2.2.12.1 - 修复TODO编号和AutoBugDetector"

# 创建标签
git tag v2.2.12.1

# 推送到远程
git push && git push origin v2.2.12.1
```

#### 步骤6：验证发布

```bash
# API验证
curl https://pypi.org/pypi/opencode-collaboration/2.2.12.1/json

# pip安装测试
pip install opencode-collaboration==2.2.12.1
```

---

## 3. Patch发布检查清单

发布前检查项：

- [ ] Bug已修复
- [ ] 单元测试通过
- [ ] pyproject.toml 版本号已更新
- [ ] CHANGELOG.md 已更新
- [ ] Git tag 已创建
- [ ] PyPI 包已上传
- [ ] API 验证通过
- [ ] pip 安装测试通过

---

## 4. Patch验收标准

### 4.1 功能验收

| 验收项 | 检查方法 |
|--------|----------|
| Bug已修复 | 手动验证原问题不再存在 |
| 无回归 | pytest tests/ 全部通过 |

### 4.2 文档验收

| 验收项 | 检查方法 |
|--------|----------|
| CHANGELOG已更新 | grep "v2.2.12.1" CHANGELOG.md |
| 版本号已更新 | grep "version" pyproject.toml |

### 4.3 发布验收

| 验收项 | 检查方法 |
|--------|----------|
| PyPI包可安装 | pip install opencode-collaboration==2.2.12.1 |
| Git标签已创建 | git tag --list \| grep v2.2.12.1 |

---

## 5. 常见问题

### Q1：如何判断一个Bug是否需要发Patch？

**判断标准**：
1. 是否影响日常开发？
2. 是否阻塞工作流程？
3. 是否需要立即修复？

如果全部是"是"，则需要发Patch。

### Q2：Patch和Minor版本有什么区别？

| 类型 | 触发条件 | 版本号变化 |
|------|----------|----------|
| Patch | Bug修复 | 2.2.12 → 2.2.12.1 |
| Minor | 新功能 | 2.2.12 → 2.2.13 |

### Q3：能否一次发布多个Bug的Patch？

**可以**。如果多个Bug同时修复：
- 版本号：2.2.12 → 2.2.12.1
- CHANGELOG中列出所有修复的Bug

---

## 6. 与其他阶段衔接

### Patch → 正常开发

1. Patch发布完成后，继续正常开发
2. 新Bug继续按Patch流程处理

### Patch → 紧急修复

1. Patch发布可随时触发
2. 不需要等待版本周期

---

## 7. 安全注意事项

### 7.1 PyPI Token

- 不要将Token写入代码
- 使用 ~/.pypirc 配置
- 设置文件权限：chmod 600 ~/.pypirc

### 7.2 版本号管理

- 不要重复发布同一版本号
- 版本号只能递增

---

## 8. 自动化建议

可以将Patch发布步骤写入脚本：

```bash
#!/bin/bash
# patch.sh

VERSION=$(grep "version" pyproject.toml | cut -d'"' -f2)
NEW_VERSION="${VERSION}.1"

echo "发布Patch: $VERSION -> $NEW_VERSION"

# 1. 更新版本号
sed -i "s/version = \"$VERSION\"/version = \"$NEW_VERSION\"/" pyproject.toml

# 2. 更新CHANGELOG
echo "## $NEW_VERSION ($(date +%Y-%m-%d))" >> CHANGELOG.md
echo "### Fixed" >> CHANGELOG.md
echo "- $1" >> CHANGELOG.md

# 3. 构建
python -m build

# 4. 上传
twine upload dist/*

# 5. Git
git add pyproject.toml CHANGELOG.md
git commit -m "fix: patch $NEW_VERSION - $1"
git tag $NEW_VERSION
git push && git push origin $NEW_VERSION

echo "✅ Patch $NEW_VERSION 已发布！"
```

---

## 9. Patch发布速查表

| 操作 | 命令 |
|------|------|
| 判断是否需要Patch | 参照1.1发布条件 |
| 创建Bug报告 | 手动创建 docs/00-memos/BUG-*.md |
| 创建Patch TODO | oc-collab todowrite --content "修复BUG-XXX" |
| 构建包 | python -m build |
| PyPI上传 | twine upload dist/* |
| API验证 | curl https://pypi.org/pypi/opencode-collaboration/{version}/json |
| pip安装 | pip install opencode-collaboration=={version} |

---

**维护者**: Agent 1
**版本**: v1.0.0
**更新日期**: 2026-02-15

---

## SOP结构概览 ⭐

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 见"1. Patch触发条件"章节 |
| **2. 操作步骤** | 见"2. Patch发布流程"章节 |
| **3. 输出产物** | v2.2.12.1, CHANGELOG.md, Git tag |
| **4. 验收标准** | 见"4. Patch验收标准"章节 |

---

## 触发条件 ⭐

**触发关键词**: `patch`, `紧急修复`, `hotfix`, `当前版本修复`

| 场景 | 触发条件 |
|------|----------|
| Patch发布 | Bug影响日常开发，需立即修复 |
| 紧急修复 | 阻塞工作流程，需24h内修复 |

---

## 操作步骤 ⭐

| 阶段 | 步骤 | 操作 | 强制 |
|------|------|------|------|
| **准备** | 1 | 判断是否需要Patch | ✅ |
| **准备** | 2 | 创建Bug报告 | ✅ |
| **准备** | 3 | 创建Patch TODO | ✅ |
| **开发** | 4 | 修复Bug | |
| **验收** | 5 | Patch验收 | ✅ |
| **发布** | 6 | 更新版本号 | ✅ |
| **发布** | 7 | 更新CHANGELOG | ✅ |
| **发布** | 8 | 构建包 | |
| **发布** | 9 | PyPI上传 | |
| **发布** | 10 | Git推送 | |
| **验证** | 11 | API验证 | ✅ |
| **验证** | 12 | pip安装测试 | ✅ |

---

## 输出产物 ⭐

| 产物 | 位置 | 格式 |
|------|------|------|
| PyPI包 | https://pypi.org/project/opencode-collaboration/ | Python包 |
| Git标签 | git tag v2.2.12.1 | Git |
| 版本提交 | git commit | Git |

---

## 验收标准 ⭐

| 标准 | 检查方法 |
|------|----------|
| Bug已修复 | 手动验证 |
| 无回归 | pytest tests/ |
| CHANGELOG已更新 | grep "v2.2.12.1" CHANGELOG.md |
| PyPI可安装 | pip install opencode-collaboration==2.2.12.1 |
