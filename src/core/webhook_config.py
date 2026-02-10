"""
WebhookConfig - Webhook配置管理模块

生成和管理Webhook配置：
- 生成Webhook配置文件
- 管理GitHub/Gitee webhook密钥
- 生成回调URL
"""

import os
import hmac
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime
import yaml


@dataclass
class WebhookServerConfig:
    host: str = "0.0.0.0"
    port: int = 8080
    endpoint: str = "/api/webhook/callback"


@dataclass
class WebhookPlatformConfig:
    secret: str = ""
    events: list = field(default_factory=list)
    enabled: bool = True


@dataclass
class WebhookConfig:
    version: str = "v1"
    github: WebhookPlatformConfig = field(default_factory=WebhookPlatformConfig)
    gitee: WebhookPlatformConfig = field(default_factory=WebhookPlatformConfig)
    server: WebhookServerConfig = field(default_factory=WebhookServerConfig)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def get_webhook_port(self) -> Optional[int]:
        return self.server.port

    def get_github_secret(self) -> str:
        return self.github.secret

    def get_gitee_secret(self) -> str:
        return self.gitee.secret

    def get_callback_url(self, base_url: str = "http://localhost") -> str:
        return f"{base_url}:{self.server.port}{self.server.endpoint}"

    def to_dict(self) -> Dict[str, Any]:
        return {
            'version': self.version,
            'webhook': {
                'github': {
                    'secret': self.github.secret,
                    'events': self.github.events,
                    'enabled': self.github.enabled
                },
                'gitee': {
                    'secret': self.gitee.secret,
                    'events': self.gitee.events,
                    'enabled': self.gitee.enabled
                },
                'server': {
                    'host': self.server.host,
                    'port': self.server.port,
                    'endpoint': self.server.endpoint
                }
            },
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class WebhookConfigError(Exception):
    """Webhook配置错误"""
    pass


class WebhookConfigManager:
    """Webhook配置管理器"""

    CONFIG_DIR = "config"
    CONFIG_FILE = "webhook.yaml"

    def __init__(self, project_path: Optional[str] = None):
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.config_file = self.project_path / self.CONFIG_DIR / self.CONFIG_FILE

    def generate_secret(self) -> str:
        return secrets.token_hex(32)

    def verify_github_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        if not signature.startswith('sha256='):
            return False
        expected = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        return hmac.compare_digest(signature, f'sha256={expected}')

    def verify_gitee_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        return hmac.compare_digest(payload, signature.encode('utf-8'))

    def generate_config(self, force: bool = False) -> WebhookConfig:
        if self.config_file.exists() and not force:
            return self.load_config()

        config = WebhookConfig(
            version="v1",
            github=WebhookPlatformConfig(
                secret=self.generate_secret(),
                events=["push", "pull_request"],
                enabled=True
            ),
            gitee=WebhookPlatformConfig(
                secret=self.generate_secret(),
                events=["push", "pull_request"],
                enabled=True
            ),
            server=WebhookServerConfig(
                host="0.0.0.0",
                port=8080,
                endpoint="/api/webhook/callback"
            )
        )

        self.save_config(config)
        return config

    def load_config(self) -> WebhookConfig:
        if not self.config_file.exists():
            raise WebhookConfigError(f"配置文件不存在: {self.config_file}")

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            webhook_data = data.get('webhook', {})
            github_data = webhook_data.get('github', {})
            gitee_data = webhook_data.get('gitee', {})
            server_data = webhook_data.get('server', {})

            return WebhookConfig(
                version=data.get('version', 'v1'),
                github=WebhookPlatformConfig(
                    secret=github_data.get('secret', ''),
                    events=github_data.get('events', []),
                    enabled=github_data.get('enabled', True)
                ),
                gitee=WebhookPlatformConfig(
                    secret=gitee_data.get('secret', ''),
                    events=gitee_data.get('events', []),
                    enabled=gitee_data.get('enabled', True)
                ),
                server=WebhookServerConfig(
                    host=server_data.get('host', '0.0.0.0'),
                    port=server_data.get('port', 8080),
                    endpoint=server_data.get('endpoint', '/api/webhook/callback')
                ),
                created_at=data.get('created_at', datetime.now().isoformat()),
                updated_at=datetime.now().isoformat()
            )
        except Exception as e:
            raise WebhookConfigError(f"加载配置文件失败: {e}")

    def save_config(self, config: WebhookConfig, path: Optional[str] = None) -> bool:
        save_path = Path(path) if path else self.config_file

        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(config.to_dict(), f, allow_unicode=True, sort_keys=False)

            return True
        except Exception as e:
            raise WebhookConfigError(f"保存配置文件失败: {e}")

    def get_status(self) -> Dict[str, Any]:
        if not self.config_file.exists():
            return {
                'configured': False,
                'github_enabled': False,
                'gitee_enabled': False,
                'port': 8080
            }

        try:
            config = self.load_config()
            return {
                'configured': True,
                'github_enabled': config.github.enabled,
                'gitee_enabled': config.gitee.enabled,
                'port': config.server.port,
                'callback_url': config.get_callback_url()
            }
        except WebhookConfigError:
            return {
                'configured': False,
                'github_enabled': False,
                'gitee_enabled': False,
                'port': 8080
            }


def main():
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Webhook配置管理")
    parser.add_argument('--init', '-i', action='store_true', help='初始化配置')
    parser.add_argument('--force', '-f', action='store_true', help='强制重新生成')
    parser.add_argument('--status', '-s', action='store_true', help='查看状态')
    parser.add_argument('--json', action='store_true', help='JSON格式输出')

    args = parser.parse_args()

    manager = WebhookConfigManager()

    if args.status:
        status = manager.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("=== Webhook配置状态 ===")
            print(f"已配置: {status['configured']}")
            print(f"GitHub启用: {status['github_enabled']}")
            print(f"Gitee启用: {status['gitee_enabled']}")
            print(f"端口: {status['port']}")
            if 'callback_url' in status:
                print(f"回调URL: {status['callback_url']}")
        return

    if args.init:
        config = manager.generate_config(force=args.force)
        if args.json:
            print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))
        else:
            print("=== Webhook配置已生成 ===")
            print(f"配置文件: {manager.config_file}")
            print(f"GitHub Secret: {config.github.secret[:8]}...")
            print(f"Gitee Secret: {config.gitee.secret[:8]}...")
            print(f"回调URL: {config.get_callback_url()}")


if __name__ == "__main__":
    main()
