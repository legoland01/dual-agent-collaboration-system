#!/usr/bin/env python3
"""
自动协作监控守护进程
持续监控 Git 变更，自动同步和推进阶段
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

LOG_FILE = "/tmp/auto_monitor.log"
PID_FILE = "/tmp/auto_monitor.pid"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024*1024, backupCount=3),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AutoMonitor:
    """自动监控器"""

    def __init__(self, project_path: str, poll_interval: int = 30):
        self.project_path = Path(project_path).resolve()
        self.poll_interval = poll_interval
        self.last_commit = self._get_last_commit()

    def _run_git(self, *args, timeout: int = 30) -> subprocess.CompletedProcess:
        """运行 git 命令"""
        try:
            return subprocess.run(
                ["git"] + list(args),
                cwd=str(self.project_path),
                capture_output=True,
                text=True,
                timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return subprocess.CompletedProcess(args, 1, "", "Command timed out")

    def _get_last_commit(self) -> str:
        """获取最后提交"""
        result = self._run_git("rev-parse", "HEAD")
        return result.stdout.strip() if result.returncode == 0 else ""

    def _get_all_remotes(self) -> list:
        """获取所有远程仓库（去重，相同URL只保留一个）"""
        result = self._run_git("remote", "-v")
        if result.returncode != 0:
            return ["origin"]

        remote_urls = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    # 保留第一个出现的远程名称（去重，保留 fetch URL）
                    if name not in remote_urls:
                        remote_urls[name] = url

        return list(remote_urls.keys())

    def _get_unique_remotes_to_push(self) -> list:
        """获取需要推送的远程列表（相同URL只推一次）"""
        result = self._run_git("remote", "-v")
        if result.returncode != 0:
            return ["origin"]

        remote_map = {}
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    url = parts[1]
                    # URL 相同时只保留第一个远程
                    if url not in remote_map:
                        remote_map[url] = name

        # 返回需要推送的远程列表
        return list(remote_map.values())

    def _has_remote_changes(self) -> bool:
        """检查远程是否有新变更"""
        result = self._run_git("fetch")
        if result.returncode != 0:
            return False

        result = self._run_git("rev-list", "--count", "HEAD..origin/main")
        if result.returncode == 0:
            return int(result.stdout.strip()) > 0
        return False

    def _has_local_changes(self) -> bool:
        """检查本地是否有未提交变更"""
        result = self._run_git("status", "--porcelain")
        return bool(result.stdout.strip())

    def _is_ahead(self) -> bool:
        """检查是否领先远程"""
        result = self._run_git("status", "-b")
        if result.returncode == 0:
            return "ahead" in result.stdout
        return False

    def sync_remote(self) -> bool:
        """同步远程变更"""
        try:
            if self._has_remote_changes():
                logger.info("发现远程新变更，拉取...")
                result = self._run_git("pull", "origin", "main")
                if result.returncode == 0:
                    logger.info("✓ 拉取成功")
                    return True
                else:
                    logger.warning(f"拉取失败: {result.stderr}")
            return False
        except Exception as e:
            logger.warning(f"同步远程失败: {e}")
            return False

    def commit_and_push(self, message: str = None) -> bool:
        """提交并推送本地变更"""
        if not self._has_local_changes() and not self._is_ahead():
            return False

        if message is None:
            message = f"auto: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        logger.info(f"提交并推送: {message}")

        # 添加
        self._run_git("add", "-A")

        # 检查是否有需要提交的内容
        status = self._run_git("status", "--porcelain")
        if not status.stdout.strip() and not self._is_ahead():
            logger.info("没有需要提交的变更")
            return True

        # 提交
        if status.stdout.strip():
            result = self._run_git("commit", "-m", message)
            if result.returncode != 0:
                if "nothing to commit" in result.stderr:
                    logger.info("没有需要提交的变更")
                else:
                    logger.warning(f"提交失败: {result.stderr}")
                    return False

        # 推送到所有远程（带重试，去重）
        remotes = self._get_unique_remotes_to_push()
        logger.info(f"推送到远程: {remotes}")

        all_success = True
        for remote in remotes:
            success = False
            for attempt in range(1, 6):
                result = self._run_git("push", remote, "main", timeout=60)
                if result.returncode == 0:
                    logger.info(f"✓ 推送到 {remote} 成功")
                    success = True
                    break
                else:
                    error_msg = result.stderr or result.stdout
                    if "Authentication failed" in error_msg or "Permission denied" in error_msg:
                        logger.error(f"权限错误，推送到 {remote} 失败")
                        all_success = False
                        break
                    if "Could not resolve host" in error_msg or "Connection" in error_msg:
                        logger.warning(f"网络问题，{30 * attempt}秒后重试...")
                        time.sleep(30 * attempt)
                        continue
                    logger.warning(f"推送到 {remote} 失败: {error_msg[:100]}")
                    time.sleep(10 * attempt)
            if not success and all_success:
                all_success = False

        return all_success

    def check_phase_advance(self) -> bool:
        """检查是否可以推进阶段"""
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
            dev = state.get('development', {})

            # 检查是否满足推进条件
            if phase == "development" and dev.get("status") == "completed":
                logger.info("开发完成，自动推进到测试阶段")
                state['phase'] = 'testing'
                with open(state_file, 'w') as f:
                    yaml.dump(state, f, allow_unicode=True)
                return True

            if phase == "testing" and test.get("pm_signoff") and test.get("dev_signoff"):
                logger.info("测试签署完成，自动推进到部署阶段")
                state['phase'] = 'deployment'
                with open(state_file, 'w') as f:
                    yaml.dump(state, f, allow_unicode=True)
                return True

            if phase == "deployment" and state.get('test', {}).get('status') == 'passed':
                logger.info("部署完成，自动推进到完成")
                state['phase'] = 'completed'
                with open(state_file, 'w') as f:
                    yaml.dump(state, f, allow_unicode=True)
                return True

            return False
        except Exception as e:
            logger.warning(f"检查阶段推进失败: {e}")
            return False

    def run(self):
        """运行监控循环"""
        # 写入 PID
        with open(PID_FILE, 'w') as f:
            f.write(str(os.getpid()))

        logger.info(f"=" * 60)
        logger.info(f"启动自动监控: {self.project_path}")
        logger.info(f"轮询间隔: {self.poll_interval}秒")
        logger.info(f"日志: {LOG_FILE}")
        logger.info(f"PID: {os.getpid()}")
        logger.info("按 Ctrl+C 停止")
        logger.info(f"{'=' * 60}")

        try:
            while True:
                try:
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    logger.info(f"[{now}] 检查变更...")

                    # 1. 同步远程
                    if self.sync_remote():
                        logger.info("  ✓ 已同步远程")

                    # 2. 检查阶段推进
                    if self.check_phase_advance():
                        logger.info("  ✓ 阶段已自动推进")

                    # 3. 提交并推送本地变更
                    if self.commit_and_push():
                        if self._is_ahead():
                            logger.info("  ⚠ 有未推送的提交")
                        else:
                            logger.info("  ✓ 已提交并推送到所有平台")

                except Exception as e:
                    logger.error(f"错误: {e}")

                time.sleep(self.poll_interval)

        except KeyboardInterrupt:
            logger.info("\n监控已停止")
        finally:
            # 清理 PID
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="自动协作监控守护进程")
    parser.add_argument(
        "--path", "-p",
        default=".",
        help="项目路径（默认当前目录）"
    )
    parser.add_argument(
        "--interval", "-i",
        type=int,
        default=30,
        help="轮询间隔秒数（默认30秒）"
    )

    args = parser.parse_args()

    project_path = Path(args.path).resolve()
    if not project_path.exists():
        logger.error(f"项目路径不存在: {project_path}")
        sys.exit(1)

    monitor = AutoMonitor(str(project_path), args.interval)
    monitor.run()


if __name__ == "__main__":
    main()
