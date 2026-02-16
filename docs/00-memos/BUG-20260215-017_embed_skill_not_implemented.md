# Bug报告: v2.2.11 --embed-skill功能未实现

**Bug ID**: BUG-20260215-017
**严重程度**: P0
**状态**: Open
**发现时间**: 2026-02-15
**发现者**: Agent 1

---

## 问题描述

v2.2.11需求文档明确要求实现`--embed-skill`功能，但该功能至今未被实现。

## 需求来源

### 需求文档
- `docs/01-requirements/requirements_v2.2.11.md` 第76行：
  > - [ ] todowrite支持 `--embed-skill` 参数，自动从Skill提取关键规则嵌入TODO

### 设计文档
- `docs/02-design/OUTLINE_v2.2.11.md` 第23行：
  > | **M2: Skill强制执行** | Skill嵌入TODO | todowrite支持--embed-skill参数嵌入Skill规则 | P0 |

- 第134行 US-002：
  > | US-002 | 作为Agent2，我希望收到TODO时能直接看到Skill规范 | todowrite --embed-skill自动嵌入规则 | P0 |

- 第144行 场景2：
  > **场景2: Skill嵌入** | Agent使用todowrite --embed-skill | 1. 执行todowrite --content "xxx" --embed-skill skill_name<br>2. 系统提取Skill关键规则<br>3. 嵌入TODO内容<br>4. 持久化 | TODO包含Skill规范内容 |

## 当前状态

| 组件 | 状态 |
|------|------|
| `src/core/skill_embedder.py` | ✅ 已实现（SkillEmbedder类） |
| `src/cli/enhanced_commands.py` todowrite命令 | ❌ 无`--embed-skill`参数 |

## 根因

v2.2.11开发阶段未完整实现设计文档中的M2模块，导致需求遗漏。

## 修复建议

1. 在`src/cli/enhanced_commands.py`的`todowrite_command`添加`--embed-skill`参数
2. 集成`SkillEmbedder`到todowrite流程
3. 实现从指定Skill提取关键规则并嵌入TODO内容
4. 补充E2E测试覆盖需求验证

---

**状态**: Open
**优先级**: P0
