import hmac
import hashlib
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class SignaturePlatform(Enum):
    """签名验证平台"""
    GITHUB = "github"
    GITEE = "gitee"


@dataclass
class ValidationResult:
    """验证结果"""
    is_valid: bool
    platform: Optional[SignaturePlatform]
    error: Optional[str] = None


class HMACValidator:
    """HMAC签名验证器"""

    GITHUB_SIGNATURE_HEADER = "X-Hub-Signature-256"
    GITEE_TOKEN_HEADER = "X-Gitee-Token"

    def __init__(self, secret: str, skip_verification: bool = False):
        """初始化验证器

        Args:
            secret: Webhook Secret
            skip_verification: 是否跳过验证（开发模式）
        """
        self.secret = secret
        self.skip_verification = skip_verification or \
            os.environ.get("OC_COLLAB_WEBHOOK_SKIP_VERIFY", "").lower() == "true"

    def validate_github(self, body: bytes, signature: str) -> ValidationResult:
        """验证GitHub Webhook签名

        Args:
            body: 请求体
            signature: X-Hub-Signature-256 header

        Returns:
            验证结果
        """
        if self.skip_verification:
            logger.debug("开发模式：跳过GitHub签名验证")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITHUB)

        if not signature:
            logger.warning("GitHub签名缺失")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Missing X-Hub-Signature-256 header"
            )

        if not signature.startswith("sha256="):
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Invalid signature format (expected sha256=)"
            )

        expected_sig = "sha256=" + hmac.new(
            self.secret.encode('utf-8'),
            body,
            hashlib.sha256
        ).hexdigest()

        if hmac.compare_digest(signature, expected_sig):
            logger.info("GitHub签名验证通过")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITHUB)
        else:
            logger.warning("GitHub签名验证失败")
            self._log_security_warning("GitHub", "signature mismatch")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITHUB,
                error="Signature mismatch"
            )

    def validate_gitee(self, body: bytes, token: str) -> ValidationResult:
        """验证Gitee Webhook签名

        Args:
            body: 请求体
            token: X-Gitee-Token header

        Returns:
            验证结果
        """
        if self.skip_verification:
            logger.debug("开发模式：跳过Gitee Token验证")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITEE)

        if not token:
            logger.warning("Gitee Token缺失")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITEE,
                error="Missing X-Gitee-Token header"
            )

        if hmac.compare_digest(token, self.secret):
            logger.info("Gitee Token验证通过")
            return ValidationResult(is_valid=True, platform=SignaturePlatform.GITEE)
        else:
            logger.warning("Gitee Token验证失败")
            self._log_security_warning("Gitee", "token mismatch")
            return ValidationResult(
                is_valid=False,
                platform=SignaturePlatform.GITEE,
                error="Token mismatch"
            )

    def validate_request(
        self,
        body: bytes,
        headers: dict
    ) -> Tuple[ValidationResult, Optional[SignaturePlatform]]:
        """综合验证请求（自动检测平台）

        Args:
            body: 请求体
            headers: 请求头

        Returns:
            (验证结果, 检测到的平台)
        """
        github_sig = headers.get(self.GITHUB_SIGNATURE_HEADER)
        gitee_token = headers.get(self.GITEE_TOKEN_HEADER)

        if github_sig:
            result = self.validate_github(body, github_sig)
            return result, SignaturePlatform.GITHUB if result.is_valid else None

        if gitee_token:
            result = self.validate_gitee(body, gitee_token)
            return result, SignaturePlatform.GITEE if result.is_valid else None

        return ValidationResult(
            is_valid=False,
            platform=None,
            error="No signature header found"
        ), None

    def _log_security_warning(self, platform: str, reason: str):
        """记录安全警告"""
        logger.warning(
            f"⚠️  [{platform.upper()}] Webhook安全警告: {reason}"
        )
