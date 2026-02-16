import re
from typing import List, Optional
from dataclasses import dataclass
from .skill_index import SkillIndex


@dataclass
class SearchResult:
    skill: str
    description: str
    keywords: List[str]
    confidence: float


class SkillSearchEngine:
    def __init__(self, index: SkillIndex):
        self.index = index
    
    def search(self, query: str, top_k: int = 3) -> List[SearchResult]:
        if not query or not query.strip():
            return []
        
        tokens = self._tokenize(query)
        if not tokens:
            return []
        
        results = []
        
        for skill in self.index.get_all_skills():
            if not skill:
                continue
            info = self.index.get_skill_info(skill)
            if not info:
                continue
            
            keywords = info.get("keywords", [])
            confidence = self._calculate_confidence(tokens, keywords)
            
            if confidence > 0:
                results.append(SearchResult(
                    skill=skill,
                    description=info.get("description", ""),
                    keywords=keywords,
                    confidence=confidence
                ))
        
        results.sort(key=lambda x: x.confidence, reverse=True)
        return results[:top_k]
    
    def _tokenize(self, query: str) -> List[str]:
        return re.findall(r'\w+', query.lower())
    
    def _calculate_confidence(self, query_tokens: List[str], keywords: List[str]) -> float:
        if not keywords:
            return 0.0
        
        keywords_lower = [k.lower() for k in keywords]
        matches = sum(1 for token in query_tokens if any(token in kw for kw in keywords_lower))
        
        if not matches:
            return 0.0
        
        keyword_match_ratio = matches / len(keywords)
        query_match_ratio = matches / len(query_tokens) if query_tokens else 0
        
        return (keyword_match_ratio + query_match_ratio) / 2
