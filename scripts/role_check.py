#!/usr/bin/env python3
"""角色边界检查脚本

在编辑文件前运行此脚本检查权限。

用法:
    python3 scripts/role_check.py <agent_id> <action> <file_path>

示例:
    python3 scripts/role_check.py agent1 edit src/core/signoff.py
    python3 scripts/role_check.py agent2 edit docs/01-requirements/REQ.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.role_boundary_checker import RoleBoundaryChecker


def main():
    if len(sys.argv) < 4:
        print(__doc__)
        sys.exit(1)

    agent_id = sys.argv[1]
    action = sys.argv[2]
    file_path = sys.argv[3]

    checker = RoleBoundaryChecker()
    result = checker.check(agent_id, action, file_path)

    print(f"\n角色边界检查结果")
    print(f"=" * 40)
    print(f"Agent: {agent_id}")
    print(f"操作: {action}")
    print(f"目标: {file_path}")
    print(f"结果: {result.result_type.value}")
    print(f"消息: {result.message}")
    print(f"=" * 40)

    if result.result_type.value == "denied":
        print("\n⛔ 权限拒绝！请不要编辑此文件。")
        print("如需修改，请创建Bug报告并分配给Agent2。")
        sys.exit(1)
    else:
        print("\n✅ 权限检查通过，可以继续操作。")
        sys.exit(0)


if __name__ == "__main__":
    main()
