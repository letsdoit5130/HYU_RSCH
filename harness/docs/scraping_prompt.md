# 범용 데이터 수집 파이프라인 스크래핑 프롬프트 & 명세서 가이드

본 문서는 특정 웹사이트 도메인에 관계없이, 범용 크롤링 및 데이터 수집 파이프라인 구축 시 필요한 프롬프트 구성 요소, **Pre/Post Hook 및 5대 검증/보안 훅 설정 기준**, 및 **@crawler-analyst-agent 에이전트 구동 프롬프트 예시**를 제공합니다.

---

## 1. 수집 타겟 네트워크 핵심 정보 정의 가이드

데이터 수집 파이프라인 구축 시 작성할 핵심 수집 프롬프트 및 헤더/파라미터 정의 구조는 다음과 같습니다.

### 1-1. 타겟 데이터 요청 URL & HTTP Method
```text
Target URL: https://example.com/api/v1/data?category={category}&page={page}
HTTP Method: GET / POST
```

### 1-2. 필수 HTTP Header 세트 (보안 인증 및 우회 패턴)
```json
{
  "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
  "Accept": "application/json, text/plain, */*",
  "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
  "Referer": "https://example.com/",
  "Authorization": "Bearer {TOKEN_PLACEHOLDER}",
  "X-Custom-Header": "{CUSTOM_KEY_IF_NEEDED}"
}
```

---

## 2. 5대 하네스 훅 & 검증 시스템 설정 스펙 (Hook Specification)

| Hook / Module 종류 | 검증 및 수행 항목 | 설정 임계값 / 규칙 (Threshold) | 실패 시 동작 (Action) |
| :--- | :--- | :--- | :--- |
| **1️⃣ Pre-Scrape Hook** | HTTP 접속 상태 & Auth | `Status Code == 200` | 401/403 시 Auth Refresh Hook 자동 호출 |
| **🔑 Auth Refresh Hook** | 토큰/쿠키 동적 갱신 | `Playwright Network Intercept` | 신규 헤더/토큰 재캡처 후 수집 재개 |
| **2️⃣ Post-Scrape Hook** | 최소 행 수 & 결측 비율 | `rows >= 10`, `Null Ratio < 50%` | 미달 시 Self-Healing Retry 메커니즘 전이 |
| **🔄 Self-Healing Retry** | 데이터 자가치유 재수집 | `max_retries = 3`, 지수 백오프 | 파라미터 보정 후 2차 수집 시도 |
| **📋 Schema Validator** | 데이터 타입 및 규격 검증 | `Pydantic / pandas type check` | 숫자/날짜 타입 불일치 수치 정제 |
| **💾 Checkpoint Manager** | 중단 지점 기록 & 이어받기 | `data/checkpoint.json` | 중단 위치(Page)부터 수집 복구 |
| **🔒 PII & Secret Guard** | 개인정보 & API Key 마스킹 | `Email, Phone, Secret Key Regex` | EDA/보고서 전이 전 `[MASKED]` 변환 |

---

## 3. @crawler-analyst-agent 호출 및 구동 프롬프트 예시

### 3-1. 에이전트 실행 프롬프트 예시
```text
"임의의 타겟 데이터 수집 및 분석 대시보드를 생성해줘.
Pre/Post Hook, 자가치유 재시도, 체크포인트 이어받기 및 보안 마스킹 훅을 포함한 파이프라인을 구축해줘."
```

### 3-2. 에이전트 트리거 및 파이프라인 연동 시나리오
1. **[Trigger Node]**: `@crawler-analyst-agent` 트리거 감지 ("웹 크롤링 분석", "크롤러 생성")
2. **[Scaffolding Step]**: `python generate_scaffolding.py` 구동으로 `data/`, `docs/`, `images/`, `src/` 스캐폴더 조립
3. **[Orchestration Step]**: `python run_pipeline.py`로 Pre-Hook -> Auth Refresh -> Scraper (Checkpoint) -> Post-Hook -> Self-Healing Retry -> Schema Validator -> PII Guard -> EDA -> Excel/Word/PPTX 일괄 실행
4. **[Output Node]**: `[CRAWLER_ANALYSIS_PIPELINE_COMPLETE]` 출력 및 산출물 링크 전달
