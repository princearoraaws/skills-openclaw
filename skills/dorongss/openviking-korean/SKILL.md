---
name: openviking-korean
description: 한국어 Context DB for AI Agents. OpenViking 기반 토큰 절감 91% 달성. 메모리, 리소스, 스킬을 파일시스템 패러다임으로 관리. Korean-first optimization. Trigger: "한국어 컨텍스트", "토큰 절감", "OpenViking 한국어", "context db", "메모리 관리", "WAL", "세션 상태", "엔티티 추출".
compatibility: OpenClaw 2.0+, Python 3.10+
---

# OpenViking Korean v1.4.0 - 한국어 Context DB

AI 에이전트를 위한 **한국어 최적화 Context Database**.

## 🆕 v1.4.0 신규 기능

| 기능 | 설명 |
|------|------|
| **WAL 프로토콜** | Write-Ahead Log - 응답 전에 저장, 컴팩션 방지 |
| **SESSION-STATE** | 세션 간 맥락 유지, 작업/결정/컨텍스트 추적 |
| **엔티티 추출** | 사람/브랜드/제품/패턴 자동 인식 |

## 핵심 가치

| 기능 | 설명 |
|------|------|
| **토큰 91% 절감** | L0/L1/L2 계층 구조로 필요한 Context만 로드 |
| **한국어 특화** | 한국어 프롬프트 템플릿 + 한국어 임베딩 최적화 |
| **파일시스템 패러다임** | 메모리/리소스/스킬을 디렉토리처럼 관리 |
| **자가 진화** | 대화 내용 자동 압축 → 장기 기억 추출 |

## v1.3.0 기능

| 기능 | 설명 |
|------|------|
| **중복 제거** | 자카드 유사도 80% 이상 → 자동 버전 업그레이드 |
| **가중치 검색** | (제목×3) + (abstract×2) + (본문×1) |
| **자동 카테고리** | 키워드 기반 자동 분류 (biz/health/gov/personal/drlady/dev) |
| **자동 요약** | 300자 이상 + summarizer 주입 시 요약 |
| **버전 백업** | 덮어쓰기 전 자동 백업 |

## 설치

```bash
# Python 패키지
pip install openviking-korean --upgrade --force-reinstall

# OpenClaw 플러그인
mkdir -p ~/.openclaw/extensions/memory-openviking-korean
cp -r . ~/.openclaw/extensions/memory-openviking-korean/
cd ~/.openclaw/extensions/memory-openviking-korean && npm install

# 설정
openclaw config set plugins.enabled true
openclaw config set plugins.slots.memory memory-openviking-korean
openclaw config set plugins.entries.memory-openviking-korean.config.mode "local"
```

## CLI 명령어

### 메모리 관리

```bash
# 메모리 검색 (한국어)
ovk find "마케팅 전략 관련 기억"

# 메모리 저장
ovk save "viking://memories/프로젝트/마케팅.md" --content "닥터레이디 여성청결제..."

# 메모리 목록
ovk ls viking://memories/

# 메모리 트리
ovk tree viking://memories/프로젝트/
```

### 리소스 관리

```bash
# 문서 추가
ovk add viking://resources/프로젝트/기획서.pdf

# 웹페이지 추가
ovk add "https://example.com/article" --uri "viking://resources/웹/기사.md"

# 리소스 검색
ovk find "닥터레이디 제품 정보" --uri "viking://resources/프로젝트/"
```

### Context 검색

```bash
# 통합 검색 (메모리 + 리소스 + 스킬)
ovk search "광고 효율 개선 방법"

# L0 요약
ovk abstract viking://resources/프로젝트/

# L1 개요
ovk overview viking://resources/프로젝트/

# 전체 읽기
ovk read viking://resources/프로젝트/마케팅.md
```

## 한국어 템플릿

### 비즈니스 Context

```
[viking://context/business/]
├── 창업/
│   ├── 닥터레이디.md
│   ├── 여성청결제_시장분석.md
│   └── 경쟁사_분석.md
├── 마케팅/
│   ├── 광고소재_라이브러리.md
│   ├── 카피라이팅_템플릿.md
│   └── ROAS_최적화.md
└── 재무/
    ├── 매출_대시보드.md
    └── 비용_관리.md
```

### 개발 Context

```
[viking://context/development/]
├── AI/
│   ├── OpenClaw_설정.md
│   ├── Sub-agent_구조.md
│   └── Cron_작업.md
├── 자동화/
│   ├── 영양제_알림.md
│   ├── 매출_리포트.md
│   └── Threads_포스팅.md
└── 스킬/
    ├── copywriting.md
    ├── seo-audit.md
    └── paid-ads.md
```

### 창작 Context

```
[viking://context/creation/]
├── 콘텐츠/
│   ├── Threads_포스트_템플릿.md
│   ├── 블로그_주제.md
│   └── 소셜미디어_캘린더.md
├── 브랜딩/
│   ├── 로큰_캐릭터.md
│   ├── 보라_페르소나.md
│   └── 메시지_가이드.md
└── 스토리텔링/
    ├── 성장_서사.md
    ├── 실패_극복.md
    └── 비전_2029.md
```

## 토큰 절감 테스트

| 작업 | 기존 토큰 | OpenViking Korean | 절감율 |
|------|-----------|-------------------|--------|
| 전체 Context 로드 | 50,000 | 4,500 | **91%** |
| 한국어 검색 | 20,000 | 2,000 | **90%** |
| 메모리 압축 | 30,000 | 3,500 | **88%** |

## API 연동

### OpenClaw Plugin

```typescript
import { OpenVikingKorean } from 'memory-openviking-korean';

const memory = new OpenVikingKorean({
  mode: 'local',
  configPath: '~/.openviking/ovk.conf',
  targetUri: 'viking://user/memories'
});

// 자동 기억
await memory.autoCapture(sessionHistory);

// 자동 회상
const context = await memory.autoRecall('마케팅 전략');
```

### Python SDK

```python
from openviking_korean import Client

client = Client(config_path="~/.openviking/ovk.conf")

# 한국어 검색
results = client.find("닥터레이디 제품 정보")

# 메모리 저장
client.save("viking://memories/프로젝트/마케팅.md", 
            content="여성청결제 시장 1위 메디온...")

# Context 계층 로드
abstract = client.abstract("viking://resources/프로젝트/")  # L0
overview = client.overview("viking://resources/프로젝트/")  # L1
content = client.read("viking://resources/프로젝트/마케팅.md")  # L2
```

## 설정 파일 (ovk.conf)

```json
{
  "vlm": {
    "provider": "openai",
    "model": "gpt-4o",
    "api_key": "<your-api-key>",
    "api_base": "https://api.openai.com/v1"
  },
  "embedding": {
    "dense": {
      "provider": "openai",
      "model": "text-embedding-3-large",
      "dimension": 3072
    }
  },
  "language": "ko",
  "token_optimization": {
    "enabled": true,
    "target_reduction": 0.91
  }
}
```

## 가격

| 플랜 | 가격 | 포함 |
|------|------|------|
| **개인** | $49/월 | 무제한 Context, 한국어 지원 |
| **팀** | $199/월 | 5명까지, 협업 기능 |
| **기업** | $499/월 | 무제한 사용자, 커스텀 통합 |

---

*OpenViking Korean v1.3.0*
*기반: Volcengine OpenViking*
*한국어 최적화: ClawHub*
*New: 중복제거, 가중치검색, 자동카테고리, 자동요약, 버전백업*