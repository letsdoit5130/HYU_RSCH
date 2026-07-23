# 📌 [FEAT] 범용 수집 및 EDA 파이프라인 하네스 정립 & data-pipeline-frame 프레임워크 개발 (Issue #1)

## 1. 이슈 개요 및 목적
특정 도메인(교보문고 등)에 종속되지 않고, 임의의 타겟 웹사이트에 대해 데이터 수집(Scraping), API 스캔(Inspect API), 사전/사후 무결성 및 자가치유 훅, 탐색적 데이터 분석(EDA) 및 엑셀/웹 대시보드와 Word/PPTX 보고서 3종을 1분 내에 자동 오케스트레이션하는 **범용 파이프라인 하네스 시스템 및 프레임워크**를 구축하고 정밀 검증합니다.

---

## 2. 세부 요구사항 및 구현 내역

### A. 하네스 정본 문서 5종 정비 (`harness/docs/`)
- `implementation_plan.md`: 범용 파이프라인 아키텍처 명세, 5대 훅 파이썬 구현 소스 코드 예시, 머메이드 플로우차트 & 11단계 시퀀스 다이어그램 작성 완수
- `scraping_prompt.md`: 5대 훅 검증 스펙표(Threshold & Action) 및 `@crawler-analyst-agent` 프롬프트 시나리오 작성
- `dashboard_plan.md`: Vanilla CSS, CORS 우회 인라인 JSON 매핑 웹/오피스 대시보드 정밀 개발 계획서 작성
- `task.md`: 하네스 7단계 구축 이력 관리 작성
- `walkthrough.md`: 범용 크롤링 및 EDA/오피스 대시보드 하네스 전방위 완료 보고서 작성

### B. 5대 핵심 검증/보안/자가치유 훅 시스템 개발
1. **Pre-Scrape Hook**: HTTP Status 200 접속 가용성 및 robots.txt 사전 스캔
2. **Auth Refresh Hook**: HTTP 401/403 세션 만료 시 Playwright 기반 토큰/쿠키 동적 자동 재캡처
3. **Post-Scrape Hook**: 수집 건수 (>= 10건) & 결측치 비율 (< 50%) 무결성 자동 검증
4. **Self-Healing Retry**: 지수 백오프(Exponential Backoff) 기반 데이터 자가치유 2차 재수집
5. **Schema & Type Validator**: Pydantic/pandas 기반 컬럼 정합성 및 숫자/날짜 타입 검증
6. **PII & Secret Guard Hook**: 이메일, 전화번호, API Secret Key 정규식 자동 마스킹 (`[MASKED]`)
7. **Checkpoint Manager**: 수집 중단 위치 기록 및 이어받기 (Resume) 백업

### C. `data-pipeline-frame/` 프레임워크 패키지 모듈화
- `engine/`, `scraping/`, `inspect_api/`, `eda/`, `dashboard/` 5대 카테고리 모듈 분리
- 모든 `.py` 파일 최상단 파이썬 한국어 Docstring 필구 규칙 100% 반영 준수

### D. 통합 테스트 하네스 검증 결과
- **5대 훅 단체 및 정량 실측 테스트 (`test_hooks.py`)**: `ALL HOOKS PASSED (100%)`
- **다중 도메인 통합 검증 (`test_harness.py`)**: `test_pipeline_demo` 및 뉴스 도메인 `naver_news_it` 실데이터 수집 및 물리 산출물 검증 `100.0% SUCCESS (6/6)` 달성

---

## 3. 상태
- **Status**: CLOSED (Pull Request #1 머제에 따라 자동 닫힘 처리)
