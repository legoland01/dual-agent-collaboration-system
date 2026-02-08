#!/bin/bash
# oc-collab 需求文档检查脚本
# 用途: 发布前检查需求文档是否完整

echo "========================================"
echo "oc-collab 需求文档检查"
echo "========================================"
echo ""

if [ -z "$1" ]; then
    echo "用法: ./check_requirements.sh <需求文档路径>"
    echo ""
    echo "示例:"
    echo "  ./check_requirements.sh docs/01-requirements/requirements_v2.2.3_READY.md"
    exit 1
fi

DOC_PATH="$1"

if [ ! -f "$DOC_PATH" ]; then
    echo "错误: 文件不存在: $DOC_PATH"
    exit 1
fi

echo "检查文档: $DOC_PATH"
echo ""

PASS=0
FAIL=0

# 检查函数
check_section() {
    local name="$1"
    local pattern="$2"

    if grep -q "$pattern" "$DOC_PATH"; then
        echo "✅ $name"
        PASS=$((PASS+1))
    else
        echo "❌ $name - 缺少必要章节"
        FAIL=$((FAIL+1))
    fi
}

# 检查状态
check_status() {
    local status=$(grep -E "^\*\*状态\*\*:" "$DOC_PATH" 2>/dev/null | head -1)

    if echo "$status" | grep -q "APPROVED"; then
        echo "✅ 文档状态: APPROVED"
        PASS=$((PASS+1))
    else
        echo "⚠️  文档状态: 非 APPROVED ($(echo $status))"
    fi
}

# 检查签署
check_signatures() {
    local agent1=$(grep -A5 "Agent 1" "$DOC_PATH" 2>/dev/null | grep "✅" | wc -l | tr -d ' ')
    local agent2=$(grep -A5 "Agent 2" "$DOC_PATH" 2>/dev/null | grep "✅" | wc -l | tr -d ' ')

    if [ "$agent1" -gt 0 ]; then
        echo "✅ Agent 1 已签署"
        PASS=$((PASS+1))
    else
        echo "❌ Agent 1 未签署"
        FAIL=$((FAIL+1))
    fi

    if [ "$agent2" -gt 0 ]; then
        echo "✅ Agent 2 已签署"
        PASS=$((PASS+1))
    else
        echo "⚠️  Agent 2 未签署 (建议评审后发布)"
    fi
}

# 检查验收标准
check_acceptance_criteria() {
    local count=$(grep -c "^\- \[ \]" "$DOC_PATH" 2>/dev/null || echo 0)

    if [ "$count" -gt 0 ]; then
        echo "✅ 验收标准: $count 项"
        PASS=$((PASS+1))
    else
        echo "⚠️  无验收标准 (建议添加)"
    fi
}

# 检查工时预估
check_effort() {
    if grep -q "工时\|总计" "$DOC_PATH"; then
        echo "✅ 有工时预估"
        PASS=$((PASS+1))
    else
        echo "❌ 无工时预估"
        FAIL=$((FAIL+1))
    fi
}

# 检查 CLI 命令清单
check_cli_commands() {
    if grep -q "CLI 命令\|新增命令" "$DOC_PATH"; then
        echo "✅ 有 CLI 命令清单"
        PASS=$((PASS+1))
    else
        echo "⚠️  无显式 CLI 命令清单"
    fi
}

# 主检查
echo "【1】基础结构检查"
echo "----------------------------------------"
check_section "概述章节" "## 1. 概述"
check_section "功能需求章节" "## 2. 功能需求"
check_section "签署确认章节" "## [0-9].*签署确认"

echo ""
echo "【2】验收标准检查"
echo "----------------------------------------"
check_acceptance_criteria

echo ""
echo "【3】工时预估检查"
echo "----------------------------------------"
check_effort

echo ""
echo "【4】CLI 命令清单检查"
echo "----------------------------------------"
check_cli_commands

echo ""
echo "【5】签署状态检查"
echo "----------------------------------------"
check_status
check_signatures

echo ""
echo "========================================"
echo "检查总结"
echo "========================================"
echo "通过: $PASS"
echo "失败: $FAIL"

if [ $FAIL -gt 0 ]; then
    echo ""
    echo "⚠️  有 $FAIL 项检查失败，建议修复后再发布"
    exit 1
else
    echo ""
    echo "✅ 检查通过，文档结构完整"
    exit 0
fi
