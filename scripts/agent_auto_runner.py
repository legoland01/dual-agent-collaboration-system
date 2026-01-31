#!/usr/bin/env python3
"""
Agent 自动执行守护进程
定期执行 oc-collab auto 命令
"""
import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from datetime import datetime
import logging
import logging.handlers

LOG_FILE = "/tmp/agent_auto.log"
PID_FILE = "/tmp/agent_auto.pid"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AgentAutoRunner:
    """Agent 自动执行器"""

    def __init__(self, project_path: str, poll_interval: int = 120):
        self.project_path = Path(project_path).resolve()
        self.poll_interval = poll_interval
        self.last_run = None

    def run_auto_command(self) -> bool:
        """执行 oc-collab auto 命令"""
        try:
            logger.info("执行 oc-collab auto...")
            
            result = subprocess.run(
                ["python3", "-m", "src.cli.main", "auto", "--max-iterations", "3"],
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                logger.info("✓ oc-collab auto 执行成功")
                if result.stdout:
                    logger.info(f"输出: {result.stdout[:500]}")
                return True
            else:
                logger.warning(f"oc-collab auto 执行失败: {result.stderr[:200]}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.warning("oc-collab auto 超时")
            return False
        except Exception as e:
            logger.error(f"执行错误: {e}")
            return False

    def check_should_run(self) -> bool:
        """检查是否应该执行"""
        state_file = self.project_path / "state" / "project_state.yaml"
        if not state_file.exists():
            return False

        try:
            import yaml
            with open(state_file, 'r') as f:
                state = yaml.safe_load(f)

            if not state:
                return False

            phase = state.get('phase', '')
            test = state.get('test', {})

            # 测试阶段：如果测试未完成，应该运行
            if phase == "testing":
                if test.get('status') == 'in_progress':
                    return True

            # 开发阶段：如果开发未完成，应该运行
            dev = state.get('development', {})
            if phase == "development" and dev.get('status') != 'completed':
                return True

            # 部署阶段
            deploy = state.get('deployment', {})
            if phase == "deployment" and deploy.get('status') == 'in_progress':
                return True

            return False

        except Exception as e:
            logger.warning(f"检查状态失败: {e}")
            return False

    def run(self):
        """运行监控循环"""
        # 写入 PID
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))

        logger.info(f"=" * 60)
        logger.info(f"启动 Agent 自动执行: {self.project_path}")
        logger.info(f"轮询间隔: {self.poll_interval}秒")
        logger.info(f"日志: {LOG_FILE}")
        logger.info(f"PID: {os.getpid()}")
        logger.info("按 Ctrl+C 停止")
        logger.info(f"{'=' * 60}")

        try:
            while True:
                try:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logger.info(f"[{now}] 检查是否需要执行...")

                    if self.check_should_run():
                        self.run_auto_command()
                    else:
                        logger.info("  当前无需执行")

                except Exception as e:
                    logger.error(f"错误: {e}")

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("\n已停止")
        finally:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Agent 自动执行守护进程")
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="项目路径（默认当前目录）"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=120,
        help="轮询间隔秒数（默认120秒）"
    )

    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.exists():
        logger.error(f"项目路径不存在: {project_path}")
        sys.exit(1)

    runner = AgentAutoRunner(str(project_path), args.interval)
    runner.run()


if __name__ == "__main__":
    main()
