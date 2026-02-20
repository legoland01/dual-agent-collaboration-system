"""
文件系统抽象层 - 用于提高可测试性
"""

import os
from pathlib import Path
from typing import List, Protocol, Iterator


class FileReader(Protocol):
    """文件读取接口"""
    def read(self, path: Path) -> str:
        """读取文件内容"""
        ...


class DirectoryScanner(Protocol):
    """目录扫描接口"""
    def iterdir(self, path: Path) -> Iterator[Path]:
        """遍历目录"""
        ...
    
    def rglob(self, path: Path, pattern: str) -> Iterator[Path]:
        """递归查找文件"""
        ...


class RealFileReader:
    """真实文件读取器"""
    def read(self, path: Path) -> str:
        return path.read_text(encoding='utf-8')


class RealDirectoryScanner:
    """真实目录扫描器"""
    def iterdir(self, path: Path) -> Iterator[Path]:
        return path.iterdir()
    
    def rglob(self, path: Path, pattern: str) -> Iterator[Path]:
        return path.rglob(pattern)


class MockFileReader:
    """模拟文件读取器 - 用于测试"""
    def __init__(self, files: dict = None):
        self.files = files or {}
    
    def read(self, path: Path) -> str:
        key = str(path)
        if key in self.files:
            return self.files[key]
        raise FileNotFoundError(f"Mock file not found: {key}")


class MockDirectoryScanner:
    """模拟目录扫描器 - 用于测试"""
    def __init__(self, structure: dict = None):
        self.structure = structure or {}
    
    def iterdir(self, path: Path) -> Iterator[Path]:
        key = str(path)
        if key in self.structure:
            for name in self.structure[key].get("dirs", []):
                yield path / name
            for name in self.structure[key].get("files", []):
                yield path / name
        return
        yield  # 确保返回迭代器
    
    def rglob(self, path: Path, pattern: str) -> Iterator[Path]:
        key = str(path)
        if key in self.structure:
            for f in self.structure[key].get("files", []):
                if f.endswith(pattern.replace("*", "")):
                    yield path / f
        return
        yield


class ExceptionFileReader:
    """异常文件读取器 - 用于测试异常处理路径"""
    def __init__(self, exception=Exception("Test exception")):
        self.exception = exception
    
    def read(self, path: Path) -> str:
        raise self.exception
