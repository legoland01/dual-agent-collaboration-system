# Proposal: BUG自动关联测试系统

**提案编号**: P-017
**提案日期**: 2026-02-15
**提案人**: Agent 1
**优先级**: P1
**来源**: TODOWRITE_BUG_SUMMARY.md

---

## 一、问题背景

### 1.1 todowrite BUG历史

| 时间 | BUG数量 | 问题类型 |
|------|---------|----------|
| v2.2.8 | 3个 | 持久化、参数传递 |
| v2.2.9 | 2个 | Skill强制、持久化 |
| v2.2.10 | 3个 | 持久化、Skill强制 |
| v2.2.11 | 5个 | TODO编号、AutoBugDetector |
| v2.2.12 | 2个 | TODO编号、AutoBugDetector |

**总计**: 15个todowrite相关BUG

### 1.2 测试覆盖现状

| 测试覆盖 | 百分比 |
|-----------|---------|
| 已有测试 | 30% |
| 缺失测试 | 70% |

### 1.3 问题根因

**每次版本发布后，测试覆盖不足，导致同类BUG反复出现**：

```
版本发布
    │
    ▼
新BUG出现
    │
    ▼
修复BUG
    │
    ▼
没有测试覆盖
    │
    ▼
下个版本
    │
    ▼
同类BUG再次出现 ❌
```

---

## 二、解决方案

### 2.1 系统设计

```
BUG创建 ──→ 系统自动检查测试覆盖
                 │
                 ├── 有测试 ──→ 标记"已覆盖"
                 │
                 └── 无测试 ──→ 自动创建测试TODO
                                      │
                                      ▼
                              Agent创建测试用例
                                      │
                                      ▼
                              测试通过 ──→ BUG标记"已验证"
```

### 2.2 核心功能

| 功能 | 说明 |
|------|------|
| BUG关联测试检查 | 创建BUG时自动检查是否有测试 |
| 测试TODO自动创建 | 无测试时自动创建测试TODO |
| 发布前检查清单 | 版本发布前自动检查覆盖 |
| 覆盖报告生成 | 生成测试覆盖报告 |

### 2.3 实现方式

#### 2.3.1 BUG模板更新

```markdown
# BUG报告模板

**BUG编号**: BUG-YYYYMMDD-XXX
...
**测试覆盖**: [待检查/已覆盖/无需测试]

---

## 测试用例

### 已有测试
- [ ] TC-XXX-001: 测试描述

### 需要创建测试
- [ ] 待创建的测试
```

#### 2.3.2 发布前检查命令

```bash
# oc-collab release --check
✓ 检查所有BUG是否有测试覆盖
✓ 运行测试套件
✓ 生成覆盖报告
✓ 检查覆盖率 >= 80%
```

#### 2.3.3 自动化检查

```python
# 创建BUG时自动检查
def create_bug_report(bug_id):
    if not has_test_coverage(bug_id):
        create_test_todo(bug_id)
        notify_agent(f"BUG-{bug_id} 需要创建测试用例")
```

---

## 三、详细设计

### 3.1 BUG报告模板更新

```markdown
# BUG报告模板

**BUG编号**: BUG-YYYYMMDD-XXX
**发现日期**: YYYY-MM-DD
**优先级**: P0/P1/P2
**状态**: OPEN
**测试覆盖**: 待检查

---

## 问题描述

### 问题现象
[问题描述]

### 影响范围
[影响哪些功能]

## 测试用例

### 已有测试
- [ ] TC-XXX-001: [测试描述] (链接)
- [ ] TC-XXX-002: [测试描述] (链接)

### 需要创建测试
- [ ] TC-XXX-003: [测试描述]
- [ ] TC-XXX-004: [测试描述]

## 修复验证

- [ ] 所有测试通过
- [ ] 回归测试通过
- [ ] 覆盖新场景
```

### 3.2 release --check 命令

```python
@click.command("release")
@click.option("--check", is_flag=True, help="检查发布条件")
@click.option("--force", is_flag=True, help="强制发布")
def release_command(check, force):
    """
    版本发布命令
    
    示例:
      oc-collab release --check    # 检查发布条件
      oc-collab release --force    # 强制发布
    """
    if check:
        # 检查测试覆盖
        coverage = check_test_coverage()
        
        # 检查BUG覆盖
        bug_coverage = check_bug_coverage()
        
        # 生成报告
        report = generate_coverage_report(coverage, bug_coverage)
        
        if report.all_passed or force:
            click.echo("✅ 可以发布")
        else:
            click.echo("❌ 不满足发布条件")
            click.echo(report.issues)
    else:
        click.echo("请使用 --check 选项")
```

### 3.3 自动化检查集成

#### 3.3.1 BUG报告创建时检查

```python
def on_bug_created(bug_id, bug_content):
    """创建BUG报告时自动检查"""
    
    # 解析BUG内容
    bug = parse_bug_report(bug_content)
    
    # 检查是否有测试覆盖
    if not has_test_coverage(bug):
        # 自动创建测试TODO
        test_todo = create_test_todo(bug)
        
        # 发送通知
        notify_agent(f"BUG-{bug_id} 需要创建测试用例")
        
        # 更新BUG报告，标记"待检查"
        update_bug_status(bug_id, "test_pending")
```

#### 3.3.2 测试创建时关联

```python
def on_test_created(test_id, bug_id):
    """创建测试时自动关联BUG"""
    
    # 关联测试与BUG
    link_test_to_bug(test_id, bug_id)
    
    # 更新BUG状态
    if all_tests_for_bug_passed(bug_id):
        update_bug_status(bug_id, "verified")
```

---

## 四、工作流程

### 4.1 新BUG处理流程

```
Agent发现BUG
        │
        ▼
创建BUG报告
        │
        ▼
系统自动检查测试覆盖
        │
        ├── 有测试 ──→ 标记"已覆盖"
        │
        └── 无测试 ──→ 创建测试TODO
                             │
                             ▼
                    Agent创建测试用例
                             │
                             ▼
                    运行测试
                             │
                             ▼
                    测试通过 ──→ BUG标记"已验证"
```

### 4.2 版本发布流程

```
版本开发完成
        │
        ▼
oc-collab release --check
        │
        ├── 测试覆盖 >= 80%
        ├── 所有BUG有测试
        └── 测试全部通过
        │
        ▼
可以发布
        │
        ▼
发布版本
        │
        ▼
更新覆盖报告
```

### 4.3 定期检查流程

```
定时任务（每小时）
        │
        ▼
检查未验证的BUG
        │
        ├── 有测试但未运行 ──→ 运行测试
        │
        └── 有测试但失败 ──→ 通知修复
```

---

## 五、验收标准

- [ ] 创建BUG时自动检查测试覆盖
- [ ] 无测试时自动创建测试TODO
- [ ] release --check 命令能检查覆盖
- [ ] 覆盖报告能生成
- [ ] 所有历史BUG都有测试覆盖
- [ ] 下个版本不会有同类BUG重复出现

---

## 六、影响范围

### 6.1 修改文件

| 文件 | 修改内容 |
|------|----------|
| `docs/templates/bug_report_template.md` | BUG报告模板增加测试用例章节 |
| `src/cli/release.py` | release --check 命令 |
| `src/core/coverage_tracker.py` | 覆盖跟踪器（新增） |
| `src/core/bug_tester_linker.py` | BUG-测试关联器（新增） |

### 6.2 新增文件

| 文件 | 说明 |
|------|------|
| `src/core/coverage_tracker.py` | 覆盖跟踪器 |
| `src/core/bug_tester_linker.py` | BUG-测试关联器 |
| `docs/templates/bug_report_template.md` | BUG报告模板 |

### 6.3 兼容性

- 不影响现有功能
- 增量功能

---

## 七、工时预估

| 任务 | 工时 |
|------|------|
| BUG报告模板更新 | 0.5h |
| 覆盖跟踪器开发 | 3h |
| BUG-测试关联器开发 | 2h |
| release --check命令 | 2h |
| 测试验证 | 1h |
| **总计** | **8.5h** |

---

## 八、关联文档

| 文档 | 说明 |
|------|------|
| `docs/00-memos/TODOWRITE_BUG_SUMMARY.md` | todowrite BUG汇总 |
| `skills/oc_collab_patch_release_guide/` | Patch发布流程 |
| `docs/01-requirements/requirements_v2.2.0.md` | 需求模板 |

---

## 九、结论

### 9.1 是否符合oc-collab边界？

- ✅ 只做CLI能做的事情
- ✅ 不增加Web UI
- ✅ 自动化程度在系统能力范围内

### 9.2 优先级

- **P1** - v2.3质量保证核心功能

### 9.3 决策

| 选项 | 选择 |
|------|------|
| ✅ 通过 | 实施BUG自动关联测试系统 |
| 拒绝 | - |
| 延期 | - |

---

**提案人**: Agent 1
**日期**: 2026-02-15
**状态**: 待评审
