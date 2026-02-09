# oc-collab 部署阶段指南

**版本**：v1.1.0  
**适用阶段**：deployment  
**Agent**：Agent 2（开发负责人）

---

## SOP结构概览

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 见"1. 部署阶段概述"章节 |
| **2. 操作步骤** | 见"2. 部署流程总览"章节 |
| **3. 输出产物** | dist/**/*.whl, dist/**/*.tar.gz, pyproject.toml |
| **4. 验收标准** | 见"6. 验证 PyPI 发布"章节 |

---

## 1. 部署阶段概述

部署阶段是开发周期最后一步，将验收通过的软件包发布到目标平台（如 PyPI）。

### v1.1.0 更新说明

**新增**：3.0 环境更新检查 - 部署前必须确认环境已更新

### 阶段入口条件

- [x] 测试验收已完成（`acceptance.status: APPROVED`）
- [x] 所有测试通过（单元测试、E2E 测试、黑盒测试）
- [x] 代码已提交并推送到远程仓库
- [x] `project_state.yaml` 中 `testing.status: completed`

### 阶段出口条件

- [x] PyPI 包已成功上传并可安装
- [x] Git 远程仓库已更新
- [x] `project_state.yaml` 中 `deployment.status: completed`

---

## 2. 部署流程总览

```
┌─────────────────────────────────────────────────────────────────┐
│                        部署阶段流程                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. 版本号升级  →  2. 构建包  →  3. 验证包内容                 │
│         │                 │                │                   │
│         ▼                 ▼                ▼                   │
│  4. PyPI 上传  ←  3. 验证包内容                                  │
│         │                                                         │
│         ▼                                                         │
│  5. Git 推送                                                    │
│                                                                 │
│         ▼                                                         │
│  6. 验证发布（API 验证 + 安装测试）                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. 部署前检查清单

### 3.0 环境更新检查 ⭐

**每次部署前必须确认环境已更新**

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 检查版本号是否更新
cat pyproject.toml | grep version

# 3. 如果版本号更新，必须重新安装
pip install -e .

# 4. 验证安装
oc-collab --help
```

**重要**：不重新安装会导致使用旧版本 CLI！

### 3.1 代码状态检查

```bash
# 1. 确认所有代码已提交
git status

# 2. 确认远程同步
git fetch origin && git log HEAD..origin/main --oneline

# 3. 确认版本状态
cat state/project_state.yaml | grep -A5 "v2.2.x"
```

### 3.2 测试状态检查

```bash
# 运行所有测试
python3 -m pytest tests/ -v --tb=short

# 检查测试覆盖率（核心模块 ≥ 80%）
python3 -m pytest tests/ --cov=src.core --cov-report=term-missing
```

### 3.3 项目状态检查

```bash
# 确认验收已完成
python3 -c "
import yaml
with open('state/project_state.yaml') as f:
    state = yaml.safe_load(f)
    
version = 'v2.2.x'  # 替换为当前版本
status = state[version]['acceptance']['status']
print(f'验收状态: {status}')
assert status == 'APPROVED', '验收未完成！'
"
```

---

## 4. 版本号管理

### 4.1 版本号规则

```
主版本.次版本.修订版本

主版本（Major）：不兼容的 API 变更
次版本（Minor）：新增功能（向后兼容）
修订版本（Patch）：Bug 修复（向后兼容）
```

### 4.2 更新版本号

编辑 `pyproject.toml`：

```toml
[project]
version = "2.2.4"  # 更新版本号
```

---

## 5. PyPI 发布

### 5.1 构建包

```bash
# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建包
python3 -m build
```

构建完成后会生成：
- `dist/opencode_collaboration-{version}-py3-none-any.whl`
- `dist/opencode_collaboration-{version}.tar.gz`

### 5.2 PyPI 配置

#### 检查配置文件

```bash
# 检查是否已配置 PyPI
cat ~/.pypirc
```

#### 配置文件格式（如果不存在）

```ini
[distutils]
index-servers = pypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmcCJ...  # 使用 API Token
```

#### 创建 API Token

1. 访问 https://pypi.org/manage/account/
2. 点击「Add API token」
3. 选择 scopes（建议：Entire account 或 Specific project）
4. 复制 token 并保存到 `~/.pypirc`

#### 安全提示

- **禁止**将 API Token 提交到代码仓库
- **禁止**在日志或输出中打印 Token
- 使用 `.gitignore` 排除敏感文件

### 5.3 上传包

```bash
# 上传到 PyPI
twine upload dist/opencode_collaboration-{version}-py3-none-any.whl
twine upload dist/opencode_collaboration-{version}.tar.gz

# 或者一次上传所有文件
twine upload dist/*
```

---

## 6. 验证 PyPI 发布

### 6.1 使用 PyPI API 验证（推荐）

PyPI 网页使用 JavaScript 渲染，无法通过普通 HTTP 工具获取。必须使用 API：

```bash
# 获取包信息
curl https://pypi.org/pypi/opencode-collaboration/{version}/json

# 完整验证脚本
curl -s https://pypi.org/pypi/opencode-collaboration/{version}/json | python3 -c "
import sys
import json

data = json.load(sys.stdin)
info = data['info']

print('='*60)
print('PyPI Package Verification')
print('='*60)
print(f\"Name: {info['name']}\")
print(f\"Version: {info['version']}\")
print(f\"Summary: {info['summary']}\")
print(f\"License: {info['license']}\")
print()
print('Files:')
for f in data['urls']:
    print(f\"  - {f['filename']} ({f['size']:,} bytes)\")
print()
print('='*60)
print('✅ Package verified successfully!')
print('='*60)
"
```

### 6.2 验证内容清单

| 验证项 | 检查方法 | 预期结果 |
|--------|----------|----------|
| 包名称 | API `info.name` | `opencode-collaboration` |
| 版本号 | API `info.version` | 与预期版本一致 |
| 描述 | API `info.summary` | 非空字符串 |
| 许可证 | API `info.license` | `MIT` |
| 分类标签 | API `info.classifiers` | 包含 Python 版本、许可证等 |
| 依赖项 | API `info.requires_dist` | 与 `pyproject.toml` 一致 |
| 下载文件 | API `urls` | wheel 和 tar.gz 都存在 |
| 文件大小 | API `urls[].size` | 合理大小 |

### 6.3 链接验证

```bash
# 验证项目链接可访问
curl -s -o /dev/null -w "%{http_code}" "https://pypi.org/project/opencode-collaboration/"
# 预期：200

# 验证 Gitee 链接（403 为反爬虫保护，正常现象）
curl -s -o /dev/null -w "%{http_code}" "https://gitee.com/zhang-xiuqin01/dual-agent-collaboration-system"
# 预期：200 或 403（403 也算正常）
```

### 6.4 安装测试

```bash
# 在新环境中安装测试
pip install opencode-collaboration=={version}

# 验证安装
pip show opencode-collaboration

# 验证 CLI 命令
oc-collab --version
```

---

## 7. 项目链接配置

在 `pyproject.toml` 中添加项目链接，便于用户访问源码、问题跟踪等：

```toml
[project.urls]
Homepage = "https://gitee.com/zhang-xiuqin01/dual-agent-collaboration-system"
Repository = "https://gitee.com/zhang-xiuqin01/dual-agent-collaboration-system"
Issues = "https://gitee.com/zhang-xiuqin01/dual-agent-collaboration-system/issues"
Changelog = "https://gitee.com/zhang-xiuqin01/dual-agent-collaboration-system/-/raw/main/docs/00-changelog/CHANGELOG.md"
```

**注意**：链接必须是可以直接访问的原始文件链接（raw URL）。

---

## 8. Git 推送

### 8.1 提交更改

```bash
# 1. 提交版本更新
git add pyproject.toml
git commit -m "chore: 版本升级至 v{x}.{y}.{z}"

# 2. 推送到所有远程（GitHub + Gitee）
oc-collab sync-all -m "chore: 版本升级至 v{x}.{y}.{z}"
```

### 8.2 标签管理（可选）

```bash
# 创建版本标签
git tag -a v{x}.{y}.{z} -m "Release v{x}.{y}.{z}"

# 推送标签
git push origin v{x}.{y}.{z}
```

---

## 9. 更新项目状态

部署完成后更新 `state/project_state.yaml`：

```python
from datetime import datetime
import yaml

with open('state/project_state.yaml', 'r') as f:
    state = yaml.safe_load(f)

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# 更新部署状态
state['v2.2.x']['deployment'] = {
    'status': 'completed',
    'started_at': '2026-02-08 xx:xx:xx',  # 开始时间
    'completed_at': now,
    'pypi_version': '2.2.x',
    'pypi_url': 'https://pypi.org/project/opencode-collaboration/2.2.x/',
    'git_commit': 'xxx1234',
}

# 保存
with open('state/project_state.yaml', 'w') as f:
    yaml.dump(state, f, allow_unicode=True, sort_keys=False)

print('✅ 部署状态已更新')
```

---

## 10. 发布检查清单

| 步骤 | 检查项 | 命令 |
|------|--------|------|
| 1 | 版本号已更新 | `grep "version" pyproject.toml` |
| 2 | 包构建成功 | `ls dist/*.whl dist/*.tar.gz` |
| 3 | PyPI 上传成功 | `twine upload` 输出 |
| 4 | API 验证通过 | `curl .../json` 返回正确信息 |
| 5 | Git 已推送 | `git remote -v` |
| 6 | 状态已更新 | `cat state/project_state.yaml` |

---

## 11. 常见问题

### Q1：PyPI 上传提示 "File already exists"

**原因**：同一版本的包已存在，无法重复上传。

**解决方案**：
- 更新版本号（Patch + 1）
- 如果是同一版本需要重新上传，先删除旧文件（PyPI 不支持删除）

### Q2：PyPI 网页无法访问，但 API 可以

**原因**：PyPI 网页使用 JavaScript 渲染，命令行工具无法处理。

**解决方案**：使用 API 验证：
```bash
curl https://pypi.org/pypi/opencode-collaboration/{version}/json
```

### Q3：twine upload 失败（HTTP 401/403）

**原因**：API Token 无效或权限不足。

**解决方案**：
1. 检查 `~/.pypirc` 配置
2. 确认 Token 未过期
3. 确认 Token 作用域包含目标项目

### Q4：pip install 失败（包不存在）

**原因**：PyPI 同步延迟（通常几秒到几分钟）。

**解决方案**：
1. 等待几分钟后重试
2. 检查版本号是否正确
3. 使用 `--verbose` 查看详细错误

### Q5：Gitee 链接返回 403

**原因**：Gitee 反爬虫机制。

**解决方案**：
- 403 是正常响应，表示链接存在
- 如需验证可访问性，使用 `curl -I` 检查响应头

---

## 12. 部署阶段命令速查

| 操作 | 命令 |
|------|------|
| 构建包 | `python3 -m build` |
| 查看 dist 文件 | `ls dist/` |
| PyPI 上传 | `twine upload dist/*` |
| API 验证 | `curl https://pypi.org/pypi/opencode-collaboration/{version}/json` |
| pip 安装 | `pip install opencode-collaboration=={version}` |
| 提交版本更新 | `git add pyproject.toml && git commit -m "chore: v{x}.{y}.{z}"` |
| Git 推送 | `git push origin main` |
| 查看状态 | `cat state/project_state.yaml` |

---

## 13. 部署阶段交付物

| 交付物 | 位置 | 检查 |
|--------|------|------|
| PyPI 包 | https://pypi.org/project/opencode-collaboration/ | ✅ |
| Git 提交 | `git log --oneline -1` | ✅ |
| 项目状态 | `state/project_state.yaml` | ✅ |
| 发布验证 | API 验证输出 | ✅ |

---

## 14. 与其他阶段衔接

### 部署 → 结束

1. 确认所有交付物已就绪
2. 更新项目状态为 `APPROVED`
3. 创建发布公告（可选）

### 部署 → 下个版本

1. 创建新版本的需求文档
2. 开始新的开发周期

---

## 15. 安全注意事项

### API Token 管理

- **不要**将 Token 写入代码仓库
- **不要**在日志或输出中打印 Token
- **不要**分享 Token给他人
- **定期**检查 Token 使用记录

### 文件权限

```bash
# 设置 pypirc 文件权限（仅当前用户可读）
chmod 600 ~/.pypirc
```

---

## 16. 自动化建议

可以将部署步骤写入脚本：

```bash
#!/bin/bash
# deploy.sh

VERSION=$(grep "version" pyproject.toml | cut -d'"' -f2)
echo "部署版本: $VERSION"

# 1. 构建
echo "1. 构建包..."
python3 -m build

# 2. 上传
echo "2. 上传 PyPI..."
twine upload dist/*

# 3. 验证
echo "3. 验证发布..."
curl -s https://pypi.org/pypi/opencode-collaboration/$VERSION/json | \
    python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"版本: {d['info']['version']}\")"

# 4. Git
echo "4. Git 提交..."
git add pyproject.toml
git commit -m "chore: 版本升级至 v$VERSION"
oc-collab sync-all -m "chore: 版本升级至 v$VERSION"

echo "✅ 部署完成！"
```

---

**维护者**：Agent 2
**版本**：v1.1.0
**更新日期**：2026-02-08

---

## SOP结构概览 ⭐

| SOP要素 | 内容 |
|---------|------|
| **1. 触发条件** | 见"1. 触发条件"章节 |
| **2. 操作步骤** | 见"2. 操作步骤"章节 |
| **3. 输出产物** | PyPI包、Git提交、版本标签 |
| **4. 验收标准** | 见"4. 验收标准"章节 |

---

## 1. 触发条件 ⭐

| 场景 | 触发条件 |
|------|----------|
| 测试已验收 | testing.status: APPROVED |
| 版本号已升级 | pyproject.toml 版本已更新 |
| Agent询问部署 | 提供部署规范 |

**参考**: "部署时机"章节

## 2. 操作步骤 ⭐

| 阶段 | 步骤 | 操作 |
|------|------|------|
| 部署前 | 1 | 确认测试验收通过 |
| 部署前 | 2 | 升级版本号 |
| 部署中 | 3 | 构建包并上传PyPI |
| 部署中 | 4 | 推送Git并打标签 |
| 部署后 | 5 | 验证发布 |
| 部署后 | 6 | 更新项目状态 |

参考详细步骤：
- "3. 部署步骤"
- "4. 验证发布"
- "13. 部署阶段交付物"

## 3. 输出产物 ⭐

| 产物 | 位置 | 格式 |
|------|------|------|
| PyPI包 | https://pypi.org/project/opencode-collaboration/ | Python包 |
| Git标签 | git tag vX.X.X | Git |
| 版本提交 | git commit | Git |

## 4. 验收标准 ⭐

| 标准 | 检查方法 |
|------|----------|
| PyPI包可安装 | pip install opencode-collaboration=={version} |
| Git标签已创建 | git tag --list |
| 版本号已更新 | grep "version" pyproject.toml |
| 项目状态已更新 | cat state/project_state.yaml |

---

## 版本历史（标准化格式）

| 版本 | 日期 | 变更 | 作者 |
|------|------|------|------|
| v1.0.0 | 2026-02-08 | 初始版本 | Agent 2 |
| v1.1.0 | 2026-02-08 | 补充FAQs和命令速查 | Agent 2 |
| v1.1.1 | 2026-02-09 | 添加SOP四要素结构（Phase2） | Agent 2 |
