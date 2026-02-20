"""
公共文档查询CLI模块

提供docs query/list/architecture命令。
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional

from .file_abstractions import FileReader, DirectoryScanner, RealFileReader, RealDirectoryScanner


class DocQuery:
    """公共文档查询"""
    
    def __init__(self, project_path: str = ".", 
                 file_reader: Optional[FileReader] = None,
                 dir_scanner: Optional[DirectoryScanner] = None):
        self.project_path = Path(project_path)
        self.docs_dir = self.project_path / "docs"
        self.file_reader = file_reader or RealFileReader()
        self.dir_scanner = dir_scanner or RealDirectoryScanner()
    
    def query(self, keyword: str) -> List[dict]:
        """搜索文档内容"""
        results = []
        
        if not self.docs_dir.exists():
            return [{"error": "docs directory not found"}]
        
        for md_file in self.dir_scanner.rglob(self.docs_dir, "*.md"):
            try:
                content = self.file_reader.read(md_file)
                if keyword.lower() in content.lower():
                    lines = content.split('\n')
                    matching_lines = [l for l in lines if keyword.lower() in l.lower()]
                    
                    results.append({
                        "file": str(md_file.relative_to(self.project_path)),
                        "snippet": matching_lines[:3],
                        "match_count": len(matching_lines)
                    })
            except Exception:
                continue
        
        return results
    
    def list_docs(self, category: Optional[str] = None) -> List[dict]:
        """列出文档"""
        docs = []
        
        if not self.docs_dir.exists():
            return [{"error": "docs directory not found"}]
        
        categories = [category] if category else ["00-memos", "01-requirements", "02-design", "03-test", "04-proposals", "05-design", "06-roadmap", "07-research"]
        
        for cat in categories:
            cat_dir = self.docs_dir / cat
            if cat_dir.exists():
                for md_file in self.dir_scanner.iterdir(cat_dir):
                    if md_file.is_file() and md_file.suffix == '.md':
                        try:
                            content = self.file_reader.read(md_file)
                            first_line = content.split('\n')[0] if content else ""
                            
                            docs.append({
                                "category": cat,
                                "file": md_file.name,
                                "path": str(md_file.relative_to(self.project_path)),
                                "title": first_line.replace("#", "").strip(),
                                "size": len(content)
                            })
                        except Exception:
                            continue
        
        return docs
    
    def get_architecture(self) -> dict:
        """获取架构信息"""
        arch_file = self.docs_dir / "00-architecture" / "CORE_ARCHITECTURE.md"
        
        if not arch_file.exists():
            return {"error": "Architecture document not found"}
        
        try:
            content = self.file_reader.read(arch_file)
            return {
                "file": str(arch_file.relative_to(self.project_path)),
                "content": content,
                "size": len(content)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def get_document(self, doc_path: str) -> dict:
        """获取指定文档内容"""
        full_path = self.project_path / doc_path
        
        if not full_path.exists():
            return {"error": f"Document not found: {doc_path}"}
        
        if not full_path.suffix == '.md':
            return {"error": "Only markdown documents are supported"}
        
        try:
            content = self.file_reader.read(full_path)
            return {
                "file": doc_path,
                "content": content,
                "size": len(content),
                "lines": len(content.split('\n'))
            }
        except Exception as e:
            return {"error": str(e)}


def get_doc_query() -> DocQuery:
    """获取DocQuery单例"""
    return DocQuery()
