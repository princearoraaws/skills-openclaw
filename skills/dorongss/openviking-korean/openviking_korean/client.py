#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenViking Korean - 한국어 + 영어 Context DB 클라이언트

토큰 절감 91% 달성을 위한 다국어 최적화 클라이언트
"""

import json
import os
import re
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime
import time
import threading

# 한국어 형태소 분석 (선택적)
try:
    from konlpy.tag import Okt
    KONLPY_AVAILABLE = True
except ImportError:
    KONLPY_AVAILABLE = False

# 영어 NLP (선택적)
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


@dataclass
class Context:
    """Context 객체"""
    uri: str
    abstract: str = ""
    content: str = ""
    level: int = 2  # L0=abstract, L1=overview, L2=detail
    category: str = "general"
    language: str = "auto"  # auto, ko, en
    version: int = 1  # 버전 관리
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    meta: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "uri": self.uri,
            "abstract": self.abstract,
            "content": self.content,
            "level": self.level,
            "category": self.category,
            "language": self.language,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "meta": self.meta
        }


class MultilingualTokenizer:
    """다국어 토크나이저 - 한국어 + 영어 지원"""
    
    def __init__(self):
        # 한국어 분석기
        self.okt = Okt() if KONLPY_AVAILABLE else None
        
        # 영어 분석기
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt', quiet=True)
                nltk.download('stopwords', quiet=True)
            self.english_stopwords = set(stopwords.words('english'))
        else:
            self.english_stopwords = set()
    
    def detect_language(self, text: str) -> str:
        """언어 감지 (한국어/영어)"""
        korean_chars = len(re.findall(r'[가-힣]', text))
        english_chars = len(re.findall(r'[a-zA-Z]', text))
        
        if korean_chars > english_chars:
            return "ko"
        elif english_chars > 0:
            return "en"
        else:
            return "ko"  # 기본값
    
    def tokenize_korean(self, text: str) -> List[str]:
        """한국어 토큰화"""
        if self.okt:
            tokens = self.okt.morphs(text, stem=True)
            filtered = [t for t in tokens if len(t) > 1]
            return filtered
        else:
            return text.split()
    
    def tokenize_english(self, text: str) -> List[str]:
        """영어 토큰화"""
        if NLTK_AVAILABLE:
            tokens = word_tokenize(text.lower())
            # 불용어 제거 + 2글자 이상
            filtered = [t for t in tokens if t.isalpha() and len(t) > 1 and t not in self.english_stopwords]
            return filtered
        else:
            # 기본 토큰화
            tokens = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
            return tokens
    
    def tokenize(self, text: str, language: str = "auto") -> List[str]:
        """다국어 토큰화"""
        if language == "auto":
            language = self.detect_language(text)
        
        if language == "ko":
            return self.tokenize_korean(text)
        else:
            return self.tokenize_english(text)
    
    def extract_keywords(self, text: str, top_n: int = 5, language: str = "auto") -> List[str]:
        """핵심 키워드 추출"""
        if language == "auto":
            language = self.detect_language(text)
        
        tokens = self.tokenize(text, language)
        
        # 빈도 기반 키워드 추출
        freq = {}
        for token in tokens:
            freq[token] = freq.get(token, 0) + 1
        
        sorted_tokens = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [t[0] for t in sorted_tokens[:top_n]]


# 한국어 전용 토크나이저 (하위 호환)
class KoreanTokenizer(MultilingualTokenizer):
    """한국어 토크나이저 (하위 호환용)"""
    pass


class SimilarityChecker:
    """자카드 유사도 기반 중복 제거"""
    
    def __init__(self, threshold: float = 0.8):
        """
        Args:
            threshold: 유사도 임계값 (0.8 = 80% 이상이면 중복으로 간주)
        """
        self.threshold = threshold
    
    def jaccard_similarity(self, text_a: str, text_b: str, tokenizer: MultilingualTokenizer) -> float:
        """자카드 유사도 계산"""
        tokens_a = set(tokenizer.tokenize(text_a))
        tokens_b = set(tokenizer.tokenize(text_b))
        
        if not tokens_a or not tokens_b:
            return 0.0
        
        intersection = tokens_a & tokens_b
        union = tokens_a | tokens_b
        
        return len(intersection) / len(union)
    
    def is_duplicate(self, new_text: str, existing_text: str, tokenizer: MultilingualTokenizer) -> bool:
        """중복 여부 확인"""
        similarity = self.jaccard_similarity(new_text, existing_text, tokenizer)
        return similarity >= self.threshold


class CategorySuggester:
    """자동 카테고리 추천"""
    
    # 카테고리 키워드 맵
    CATEGORY_MAP = {
        "biz": ["매출", "ROAS", "광고", "마케팅", "CS", "주문", "매출", "객단가", "전환율", "ROAS", "CPA", "CTR"],
        "health": ["영양제", "운동", "수면", "피로", "복싱", "웨이트", "마그네슘", "단식", "IF"],
        "gov": ["특허", "지원사업", "정부", "신청", "지원금", "과제"],
        "personal": ["여자친구", "설현", "찬혁", "밤토리", "장꾸", "영현"],
        "drlady": ["이너앰플", "클렌저", "PDRN", "글루타티온", "유산균", "닥터레이디"],
        "dev": ["API", "코드", "Python", "클래스", "함수", "버그", "에러"]
    }
    
    def suggest(self, text: str, tokenizer: MultilingualTokenizer) -> str:
        """텍스트 기반 카테고리 추천"""
        tokens = set(tokenizer.tokenize(text))
        
        scores = {}
        for category, keywords in self.CATEGORY_MAP.items():
            matches = tokens & set(keywords)
            scores[category] = len(matches)
        
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]
        
        # 매칭이 없으면 기본값
        return best_category if best_score > 0 else "memories"


class WALManager:
    """Write-Ahead Log 프로토콜 - 응답 전에 먼저 저장"""
    
    def __init__(self, wal_path: str = "./wal.json"):
        self.wal_path = Path(wal_path)
        self._lock = threading.Lock()
    
    def begin_transaction(self, operation: str, data: Dict[str, Any]) -> str:
        """트랜잭션 시작 - 작업 로깅"""
        transaction_id = f"tx_{int(time.time() * 1000)}"
        
        wal_entry = {
            "id": transaction_id,
            "operation": operation,
            "data": data,
            "status": "pending",
            "timestamp": datetime.now().isoformat()
        }
        
        with self._lock:
            self._append_wal(wal_entry)
        
        return transaction_id
    
    def commit(self, transaction_id: str):
        """트랜잭션 커밋"""
        with self._lock:
            entries = self._read_wal()
            for entry in entries:
                if entry["id"] == transaction_id:
                    entry["status"] = "committed"
            self._write_wal(entries)
    
    def rollback(self, transaction_id: str):
        """트랜잭션 롤백"""
        with self._lock:
            entries = self._read_wal()
            for entry in entries:
                if entry["id"] == transaction_id:
                    entry["status"] = "rolledback"
            self._write_wal(entries)
    
    def get_pending(self) -> List[Dict[str, Any]]:
        """대기 중인 트랜잭션 조회"""
        entries = self._read_wal()
        return [e for e in entries if e["status"] == "pending"]
    
    def _append_wal(self, entry: Dict[str, Any]):
        """WAL에 항목 추가"""
        entries = self._read_wal()
        entries.append(entry)
        self._write_wal(entries)
    
    def _read_wal(self) -> List[Dict[str, Any]]:
        """WAL 읽기"""
        if self.wal_path.exists():
            try:
                with open(self.wal_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _write_wal(self, entries: List[Dict[str, Any]]):
        """WAL 쓰기"""
        self.wal_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.wal_path, 'w', encoding='utf-8') as f:
            json.dump(entries, f, ensure_ascii=False, indent=2)


class SessionStateManager:
    """SESSION-STATE.md 관리 - 세션 간 맥락 유지"""
    
    TEMPLATE = """# SESSION-STATE.md — Active Working Memory

This file is the agent's "RAM" — survives compaction, restarts, distractions.

## Current Task
{current_task}

## Key Context
{key_context}

## Pending Actions
{pending_actions}

## Recent Decisions
{recent_decisions}

---
*Last updated: {timestamp}*
"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)
        self.session_file = self.workspace_path / "SESSION-STATE.md"
        
        if not self.session_file.exists():
            self._init_session()
    
    def _init_session(self):
        """세션 파일 초기화"""
        self.session_file.parent.mkdir(parents=True, exist_ok=True)
        self.save_session(
            current_task="[None]",
            key_context="[None yet]",
            pending_actions="- [ ] None",
            recent_decisions="[None yet]"
        )
    
    def save_session(self, current_task: str = "", key_context: str = "", 
                     pending_actions: str = "", recent_decisions: str = ""):
        """세션 상태 저장 (WAL: 응답 전에 호출!)"""
        content = self.TEMPLATE.format(
            current_task=current_task or "[None]",
            key_context=key_context or "[None yet]",
            pending_actions=pending_actions or "- [ ] None",
            recent_decisions=recent_decisions or "[None yet]",
            timestamp=datetime.now().isoformat()
        )
        
        with open(self.session_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def load_session(self) -> Dict[str, str]:
        """세션 상태 로드"""
        if not self.session_file.exists():
            return {
                "current_task": "[None]",
                "key_context": "[None yet]",
                "pending_actions": "- [ ] None",
                "recent_decisions": "[None yet]"
            }
        
        with open(self.session_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 파싱
        result = {}
        sections = ["Current Task", "Key Context", "Pending Actions", "Recent Decisions"]
        
        for i, section in enumerate(sections):
            pattern = rf"## {section}\s*\n(.*?)(?=\n##|\n---)"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                result[section.lower().replace(" ", "_")] = match.group(1).strip()
            else:
                result[section.lower().replace(" ", "_")] = ""
        
        return result
    
    def update_task(self, task: str):
        """현재 작업 업데이트"""
        session = self.load_session()
        session["current_task"] = task
        self.save_session(**session)
    
    def add_context(self, context: str):
        """키 컨텍스트 추가"""
        session = self.load_session()
        existing = session.get("key_context", "")
        if existing == "[None yet]":
            existing = ""
        session["key_context"] = f"{existing}\n- {context}".strip()
        self.save_session(**session)
    
    def add_decision(self, decision: str):
        """결정 추가"""
        session = self.load_session()
        existing = session.get("recent_decisions", "")
        if existing == "[None yet]":
            existing = ""
        timestamp = datetime.now().strftime("%H:%M")
        session["recent_decisions"] = f"{existing}\n- [{timestamp}] {decision}".strip()
        self.save_session(**session)


class EntityExtractor:
    """엔티티 추출 - 사람/브랜드/제품 자동 인식"""
    
    # 사전 정의 엔티티
    KNOWN_ENTITIES = {
        "person": ["명진", "설현", "영현", "찬혁", "마스터", "보라"],
        "brand": ["Dr.Lady", "닥터레이디", "메디큐브", "비오템"],
        "product": ["이너앰플", "이너 클렌저", "클렌저", "앰플", "PDRN"],
        "pet": ["밤토리", "장꾸"],
        "org": ["바른연구소", "식약처", "ClawHub"]
    }
    
    # 패턴 기반 추출
    PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{2,3}[-.\s]?\d{3,4}[-.\s]?\d{4}\b',
        "url": r'https?://[^\s<>"{}|\\^`\[\]]+',
        "date": r'\b\d{4}[-./]\d{1,2}[-./]\d{1,2}\b|\b\d{1,2}[-./]\d{1,2}[-./]\d{4}\b',
        "money_krw": r'\b\d{1,3}(,\d{3})*원\b|\b\d+만원\b|\b\d+억원\b',
        "percent": r'\b\d+(\.\d+)?%\b',
        "hashtag": r'#[\w가-힣]+'
    }
    
    def extract(self, text: str, tokenizer: Optional[MultilingualTokenizer] = None) -> Dict[str, List[str]]:
        """텍스트에서 엔티티 추출"""
        entities = {category: [] for category in self.KNOWN_ENTITIES}
        entities["pattern"] = {}
        
        # 사전 정의 엔티티 매칭
        text_lower = text.lower()
        for category, names in self.KNOWN_ENTITIES.items():
            for name in names:
                if name.lower() in text_lower or name in text:
                    entities[category].append(name)
        
        # 패턴 기반 추출
        for pattern_name, pattern in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                entities["pattern"][pattern_name] = list(set(matches))
        
        # NER 기반 추가 추출 (tokenizer 있을 때)
        if tokenizer and KONLPY_AVAILABLE:
            nouns = tokenizer.okt.nouns(text) if tokenizer.okt else []
            # 사람 이름 패턴 (2-3글자 한글)
            potential_names = [n for n in nouns if 2 <= len(n) <= 3 and re.match(r'^[가-힣]+$', n)]
            # 이미 알려진 것 제외
            known_flat = [n.lower() for names in self.KNOWN_ENTITIES.values() for n in names]
            new_names = [n for n in potential_names if n.lower() not in known_flat]
            if new_names:
                entities["potential_person"] = list(set(new_names))[:5]  # 최대 5개
        
        # 빈 리스트 제거
        entities = {k: v for k, v in entities.items() if v}
        
        return entities
    
    def get_persons(self, text: str) -> List[str]:
        """사람만 추출"""
        entities = self.extract(text)
        return entities.get("person", []) + entities.get("potential_person", [])
    
    def get_products(self, text: str) -> List[str]:
        """제품만 추출"""
        entities = self.extract(text)
        return entities.get("product", [])
    
    def get_brands(self, text: str) -> List[str]:
        """브랜드만 추출"""
        entities = self.extract(text)
        return entities.get("brand", [])


class VersionBackup:
    """버전 백업 관리자"""
    
    def __init__(self, backup_dir: str = "./backup_memories"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup(self, file_path: Path, uri: str) -> Optional[Path]:
        """파일 백업"""
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        safe_uri = uri.replace("/", "_").replace("\\", "_")
        backup_path = self.backup_dir / f"{timestamp}_{safe_uri}.json"
        
        shutil.copy(file_path, backup_path)
        print(f"(System) 백업 완료: {backup_path}")
        
        return backup_path
    
    def list_backups(self, uri: Optional[str] = None) -> List[Path]:
        """백업 목록 조회"""
        if uri:
            safe_uri = uri.replace("/", "_").replace("\\", "_")
            return list(self.backup_dir.glob(f"*_{safe_uri}.json"))
        return list(self.backup_dir.glob("*.json"))


class CacheManager:
    """캐시 관리자 - TTL 기반 캐싱"""
    
    def __init__(self, ttl: int = 300):
        """
        Args:
            ttl: 캐시 유효시간 (초), 기본 5분
        """
        self._cache: Dict[str, tuple] = {}  # (data, timestamp)
        self._ttl = ttl
    
    def get(self, key: str) -> Optional[Any]:
        """캐시 조회"""
        if key in self._cache:
            data, timestamp = self._cache[key]
            if time.time() - timestamp < self._ttl:
                return data
            else:
                # 만료된 캐시 삭제
                del self._cache[key]
        return None
    
    def set(self, key: str, data: Any):
        """캐시 저장"""
        self._cache[key] = (data, time.time())
    
    def delete(self, key: str):
        """캐시 삭제"""
        self._cache.pop(key, None)
    
    def clear(self):
        """전체 캐시 삭제"""
        self._cache.clear()
    
    def size(self) -> int:
        """캐시 크기"""
        return len(self._cache)


class ContextStore:
    """Context 저장소 - 파일시스템 기반 + 캐싱 + 가중치 검색"""
    
    def __init__(self, base_path: str = "~/.openviking/korean", cache_ttl: int = 300):
        self.base_path = Path(base_path).expanduser()
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        # 캐시 매니저
        self._cache = CacheManager(ttl=cache_ttl)
        
        # 중복 제거
        self.similarity_checker = SimilarityChecker()
        
        # 버전 백업
        self.version_backup = VersionBackup(str(self.base_path / "backups"))
        
        # 카테고리 디렉토리 생성
        for category in ["memories", "resources", "skills", "biz", "health", "gov", "personal", "drlady", "dev"]:
            (self.base_path / category).mkdir(exist_ok=True)
    
    def save(self, context: Context, tokenizer: Optional[MultilingualTokenizer] = None, check_duplicate: bool = True) -> bool:
        """Context 저장 (중복 제거 + 버전 백업 + 캐시 무효화)"""
        try:
            # 토크나이저
            if tokenizer is None:
                tokenizer = MultilingualTokenizer()
            
            # URI에서 파일 경로 생성
            path = self._uri_to_path(context.uri)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 중복 체크
            if check_duplicate and path.exists():
                with open(path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                existing_text = existing_data.get("content", "")
                if self.similarity_checker.is_duplicate(context.content, existing_text, tokenizer):
                    # 80% 이상 유사 → 덮어쓰기 (버전 증가)
                    print(f"(System) 유사한 내용 감지, 버전 업그레이드: v{existing_data.get('version', 1)} → v{existing_data.get('version', 1) + 1}")
                    context.version = existing_data.get("version", 1) + 1
                    
                    # 백업
                    self.version_backup.backup(path, context.uri)
            
            # JSON으로 저장
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(context.to_dict(), f, ensure_ascii=False, indent=2)
            
            # 캐시 무효화
            self._cache.delete(f"load:{context.uri}")
            self._cache.delete(f"search:{context.category}")
            
            return True
        except PermissionError as e:
            raise IOError(f"파일 쓰기 권한 없음: {path}")
        except json.JSONEncodeError as e:
            raise ValueError(f"JSON 인코딩 실패: {e}")
        except Exception as e:
            raise IOError(f"저장 실패: {e}")
    
    def load(self, uri: str, level: int = 2, use_cache: bool = True) -> Optional[Context]:
        """Context 로드 (계층적 + 캐싱)"""
        cache_key = f"load:{uri}:{level}"
        
        # 캐시 확인
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        path = self._uri_to_path(uri)
        
        if not path.exists():
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 레벨에 따른 내용 로드
            context = Context(**data)
            if level == 0:
                context.content = context.abstract
            elif level == 1:
                context.content = self._get_overview(context)
            
            # 캐시 저장
            if use_cache:
                self._cache.set(cache_key, context)
            
            return context
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 실패: {path}")
        except Exception as e:
            raise IOError(f"로드 실패: {e}")
        
        return context
    
    def search(self, query: str, category: Optional[str] = None, use_cache: bool = True, tokenizer: Optional[MultilingualTokenizer] = None) -> List[tuple]:
        """다국어 검색 + 캐싱 + 가중치 스코어링
        
        Returns:
            List of (Context, score) tuples sorted by score descending
        """
        cache_key = f"search:{query}:{category}"
        
        # 캐시 확인
        if use_cache:
            cached = self._cache.get(cache_key)
            if cached:
                return cached
        
        results = []
        search_path = self.base_path / category if category else self.base_path
        
        # 토크나이저
        if tokenizer is None:
            tokenizer = MultilingualTokenizer()
        
        # 검색어 토큰화
        query_tokens = set(tokenizer.tokenize(query))
        
        # 파일 검색
        for file in search_path.rglob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 가중치 점수 계산
                score = self._calculate_search_score(query_tokens, data, tokenizer)
                
                if score > 0:
                    context = Context(**data)
                    results.append((context, score))
            except json.JSONDecodeError:
                continue
            except Exception:
                continue
        
        # 점수 순 정렬
        results.sort(key=lambda x: x[1], reverse=True)
        
        # 캐시 저장
        if use_cache:
            self._cache.set(cache_key, results)
        
        return results
    
    def _calculate_search_score(self, query_tokens: set, data: Dict, tokenizer: MultilingualTokenizer) -> float:
        """가중치 검색 점수 계산
        
        점수 = (제목 매칭 × 3) + (키워드 매칭 × 2) + (본문 매칭 × 1)
        """
        score = 0.0
        
        # 제목 (URI) 매칭 × 3
        uri = data.get("uri", "")
        uri_tokens = set(tokenizer.tokenize(uri))
        title_match = len(query_tokens & uri_tokens)
        score += title_match * 3
        
        # abstract 매칭 × 2
        abstract = data.get("abstract", "")
        abstract_tokens = set(tokenizer.tokenize(abstract))
        abstract_match = len(query_tokens & abstract_tokens)
        score += abstract_match * 2
        
        # 본문 매칭 × 1
        content = data.get("content", "")
        content_tokens = set(tokenizer.tokenize(content))
        content_match = len(query_tokens & content_tokens)
        score += content_match * 1
        
        return score
    
    def clear_cache(self):
        """캐시 전체 삭제"""
        self._cache.clear()
    
    def cache_size(self) -> int:
        """캐시 크기"""
        return self._cache.size()
    
    def _uri_to_path(self, uri: str) -> Path:
        """URI를 파일 경로로 변환"""
        # viking://memories/프로젝트/마케팅.md -> memories/프로젝트/마케팅.json
        if uri.startswith("viking://"):
            uri = uri[9:]  # viking:// 제거
        return self.base_path / f"{uri}.json"
    
    def _get_overview(self, context: Context) -> str:
        """개요 생성 (L1)"""
        # 간단한 개요 생성 로직
        lines = context.content.split('\n')
        overview_lines = lines[:10]  # 첫 10줄
        return '\n'.join(overview_lines)


class OpenVikingKorean:
    """OpenViking Korean 메인 클래스 + 다국어 지원 + 캐싱 + 에러 처리 + 자동 요약 + 자동 카테고리 + WAL + SESSION-STATE + 엔티티 추출"""
    
    def __init__(self, config_path: str = "~/.openviking/ovk.conf", cache_ttl: int = 300, 
                 summarizer: Optional[Callable] = None, workspace_path: str = "."):
        self.config_path = Path(config_path).expanduser()
        self.config = self._load_config()
        self.store = ContextStore(cache_ttl=cache_ttl)
        self.tokenizer = MultilingualTokenizer()  # 다국어 토크나이저
        
        # 자동 요약 함수 (외부 주입)
        self.summarizer = summarizer
        
        # 자동 카테고리 추천
        self.category_suggester = CategorySuggester()
        
        # WAL 프로토콜 (NEW!)
        self.wal = WALManager(wal_path=str(Path(workspace_path) / "wal.json"))
        
        # 세션 상태 관리 (NEW!)
        self.session_state = SessionStateManager(workspace_path=workspace_path)
        
        # 엔티티 추출 (NEW!)
        self.entity_extractor = EntityExtractor()
    
    def _load_config(self) -> Dict[str, Any]:
        """설정 로드 (에러 처리 강화)"""
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except json.JSONDecodeError:
            pass  # 기본 설정 사용
        except Exception:
            pass  # 기본 설정 사용
        
        return {
            "language": "auto",  # auto, ko, en
            "token_optimization": {
                "enabled": True,
                "target_reduction": 0.91
            }
        }
    
    def save_memory(self, uri: str, content: str, category: str = "auto", language: str = "auto", check_duplicate: bool = True) -> bool:
        """기억 저장 (에러 처리 + 언어 자동 감지 + 자동 요약 + 자동 카테고리 + 중복 체크)"""
        try:
            # 언어 자동 감지
            if language == "auto":
                language = self.tokenizer.detect_language(content)
            
            # 자동 카테고리 추천
            if category == "auto":
                category = self.category_suggester.suggest(content, self.tokenizer)
            
            # 자동 요약 (300자 이상 + summarizer 있을 때)
            processed_content = self._auto_summarize(content)
            
            # 다국어 요약 생성
            abstract = self._generate_abstract(processed_content, language=language)
            
            context = Context(
                uri=f"{category}/{uri}",
                abstract=abstract,
                content=processed_content,
                category=category,
                language=language
            )
            
            return self.store.save(context, tokenizer=self.tokenizer, check_duplicate=check_duplicate)
        except Exception as e:
            raise IOError(f"메모리 저장 실패: {e}")
    
    def _auto_summarize(self, text: str) -> str:
        """자동 요약 (300자 이상일 때만 작동)"""
        if len(text) > 300 and self.summarizer:
            print(f"(System) 긴 텍스트 감지: {len(text)}자 → 지능형 요약 가동...")
            return self.summarizer(text)
        return text
    
    def find(self, query: str, category: Optional[str] = None, level: int = 2, use_cache: bool = True, limit: int = 10) -> List[Dict[str, Any]]:
        """Context 검색 (캐싱 적용 + 가중치 스코어링)"""
        results = self.store.search(query, category, use_cache=use_cache, tokenizer=self.tokenizer)
        
        # 토큰 절감을 위해 레벨에 따른 내용 반환
        return [
            {
                "uri": r.uri,
                "abstract": r.abstract,
                "content": r.content if level == 2 else r.abstract,
                "category": r.category,
                "score": score,
                "version": r.version
            }
            for r, score in results[:limit]
        ]
    
    def clear_cache(self):
        """전체 캐시 삭제"""
        self.store.clear_cache()
    
    def cache_size(self) -> int:
        """캐시 크기"""
        return self.store.cache_size()
    
    def list_backups(self, uri: Optional[str] = None) -> List[str]:
        """백업 목록 조회"""
        backups = self.store.version_backup.list_backups(uri)
        return [str(b) for b in backups]
    
    def suggest_category(self, text: str) -> str:
        """카테고리 추천 (미리보기)"""
        return self.category_suggester.suggest(text, self.tokenizer)
    
    # ============ WAL + SESSION-STATE 메서드 (NEW!) ============
    
    def save_memory_wal(self, uri: str, content: str, category: str = "auto", 
                         language: str = "auto", check_duplicate: bool = True) -> bool:
        """WAL 프로토콜로 저장 - 응답 전에 호출!"""
        # 1. 트랜잭션 시작
        tx_id = self.wal.begin_transaction("save_memory", {
            "uri": uri,
            "category": category,
            "content_length": len(content)
        })
        
        try:
            # 2. 실제 저장 실행
            result = self.save_memory(uri, content, category, language, check_duplicate)
            
            # 3. 커밋
            self.wal.commit(tx_id)
            
            return result
        except Exception as e:
            # 4. 실패 시 롤백
            self.wal.rollback(tx_id)
            raise e
    
    def update_session_task(self, task: str):
        """세션 작업 업데이트 (WAL: 응답 전에 호출!)"""
        self.session_state.update_task(task)
    
    def add_session_context(self, context: str):
        """세션 컨텍스트 추가"""
        self.session_state.add_context(context)
    
    def add_session_decision(self, decision: str):
        """세션 결정 추가"""
        self.session_state.add_decision(decision)
    
    def load_session(self) -> Dict[str, str]:
        """세션 상태 로드"""
        return self.session_state.load_session()
    
    # ============ 엔티티 추출 메서드 (NEW!) ============
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """엔티티 추출"""
        return self.entity_extractor.extract(text, self.tokenizer)
    
    def extract_persons(self, text: str) -> List[str]:
        """사람 추출"""
        return self.entity_extractor.get_persons(text)
    
    def extract_products(self, text: str) -> List[str]:
        """제품 추출"""
        return self.entity_extractor.get_products(text)
    
    def extract_brands(self, text: str) -> List[str]:
        """브랜드 추출"""
        return self.entity_extractor.get_brands(text)
    
    # ============ 기존 메서드 ============
    
    def abstract(self, uri: str) -> str:
        """L0 요약 반환"""
        context = self.store.load(uri, level=0)
        return context.abstract if context else ""
    
    def overview(self, uri: str) -> str:
        """L1 개요 반환"""
        context = self.store.load(uri, level=1)
        return context.content if context else ""
    
    def read(self, uri: str) -> str:
        """L2 전체 내용 반환"""
        context = self.store.load(uri, level=2)
        return context.content if context else ""
    
    def compress_memory(self, content: str, language: str = "auto") -> str:
        """기억 압축 - 토큰 절감 (다국어)"""
        if language == "auto":
            language = self.tokenizer.detect_language(content)
        
        # 간단한 구현: 첫 500자
        compressed = content[:500]
        
        # 토큰 절감률 계산
        original_tokens = len(content.split())
        compressed_tokens = len(compressed.split())
        reduction = 1 - (compressed_tokens / original_tokens) if original_tokens > 0 else 0
        
        print(f"토큰 절감: {reduction:.1%}")
        
        return compressed
    
    def _generate_abstract(self, content: str, language: str = "auto") -> str:
        """다국어 요약 생성"""
        if language == "auto":
            language = self.tokenizer.detect_language(content)
        
        # 키워드 기반 간단한 요약
        keywords = self.tokenizer.extract_keywords(content, top_n=5, language=language)
        abstract = f"[{'/'.join(keywords)}] {content[:100]}..."
        return abstract
    
    def _calculate_relevance(self, query: str, context: Context) -> float:
        """관련도 계산 (다국어)"""
        query_keywords = set(self.tokenizer.extract_keywords(query))
        content_keywords = set(self.tokenizer.extract_keywords(context.content))
        
        if not query_keywords or not content_keywords:
            return 0.0
        
        intersection = query_keywords & content_keywords
        union = query_keywords | content_keywords
        
        return len(intersection) / len(union)


# CLI 진입점
def main():
    """CLI 메인 함수"""
    import argparse
    
    parser = argparse.ArgumentParser(description="OpenViking Korean CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # find 명령어
    find_parser = subparsers.add_parser("find", help="Context 검색")
    find_parser.add_argument("query", help="검색 쿼리")
    find_parser.add_argument("--category", "-c", help="카테고리 필터")
    find_parser.add_argument("--level", "-l", type=int, default=2, help="Context 레벨 (0=abstract, 1=overview, 2=detail)")
    
    # save 명령어
    save_parser = subparsers.add_parser("save", help="Context 저장")
    save_parser.add_argument("uri", help="저장 URI")
    save_parser.add_argument("--content", "-c", required=True, help="내용")
    save_parser.add_argument("--category", "-C", default="memories", help="카테고리")
    
    # read 명령어
    read_parser = subparsers.add_parser("read", help="Context 읽기")
    read_parser.add_argument("uri", help="읽을 URI")
    
    # abstract 명령어
    abstract_parser = subparsers.add_parser("abstract", help="L0 요약")
    abstract_parser.add_argument("uri", help="URI")
    
    # overview 명령어
    overview_parser = subparsers.add_parser("overview", help="L1 개요")
    overview_parser.add_argument("uri", help="URI")
    
    args = parser.parse_args()
    
    client = OpenVikingKorean()
    
    if args.command == "find":
        results = client.find(args.query, args.category, args.level)
        for r in results:
            print(f"[{r['relevance']:.2f}] {r['uri']}")
            print(f"  {r['abstract']}")
    
    elif args.command == "save":
        client.save_memory(args.uri, args.content, args.category)
        print(f"저장 완료: {args.uri}")
    
    elif args.command == "read":
        content = client.read(args.uri)
        print(content)
    
    elif args.command == "abstract":
        abstract = client.abstract(args.uri)
        print(abstract)
    
    elif args.command == "overview":
        overview = client.overview(args.uri)
        print(overview)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()