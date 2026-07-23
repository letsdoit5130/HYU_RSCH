# AI-Developer-KIT — Operating Contract (전 도구 공용)

> 이 파일은 이 작업 폴더에서 동작하는 **모든 에이전트형 AI 도구**의 운영 계약입니다.
> **Claude Code · Cursor · Codex · Google Antigravity** 등 어떤 도구로 이 폴더를 열든,
> 세션 시작 시 이 파일을 읽고 아래 규칙을 따릅니다.
> (Antigravity는 `GEMINI.md`도 함께 읽습니다 · Claude Code는 `.claude/CLAUDE.md`를 우선 로드합니다.)

## 세션 시작 시 (필수)

1. 이 `AGENTS.md`(운영 계약)를 로드한다.
2. 같은 폴더에 있으면 함께 읽는다: `.claude/CLAUDE.md`(상세 라우팅 룰) · `prompts/00_router_v3.md`(라우터 정본) · `START_HERE.md`(온보딩). **없어도 이 `AGENTS.md`만으로 동작한다** — 아래 계약이 자족적이다.
3. 사용자 메시지가 아래 **라우터 트리거**(특히 **"지침에 따라 진행해"**)에 해당하면 즉시 Router Contract를 활성화한다.

> **한 폴더 원칙**: KIT는 지금 열린 이 폴더에서 동작한다. 도구를 바꿀 필요가 없다 — 이 폴더를 여는 어떤 도구(Claude Code·Cursor·Codex·Antigravity)에서든 같은 계약이 적용된다. 사용자는 도구의 채팅창에 자연어로 지시하고, 도구가 필요한 터미널 명령을 대신 실행한다.

> **트랙 구분:** 이 배송본은 **Builder Track**(개발 KIT)입니다. 마케팅(AI-MARKETING)·RFP/자금(BIDS)은 별도 라이선스 팩이며, 이 폴더엔 포함되지 않습니다.

## 🚦 Router Contract v3 (Mandatory)

모든 짧은 지시어에 대해 반드시 Phase를 먼저 판별하고 태그 블록을 출력합니다.

**트리거 (이 패턴이 오면 라우터 강제 활성화):**
- "지침에 따라서", "가이드대로", "정본대로"
- "진행해", "계속해", "가능해?"
- "확인해봐", "다 된거야?", "끝났어?", "끝이야?"
- "문서화", "정리해", "업데이트 했어?"
- "고도화", "스프린트", "iteration", "다음 버전"
- "너가 해", "해결해", "커밋하고 배포해"
- "장문 프롬프트", "프롬프트 날린 것", "채팅 기반 스킬화"

**응답 순서 (강제):**
1. 첫 줄: `[ROUTER]`
2. 둘째 줄: 아래 중 하나의 완성형 블록
3. 마지막: 질문 1개 (필요한 경우만)

```
Gate (Phase 4):
[GATE]: OPEN / HOLD
[VALUE]: PASS / HOLD
[RESOURCE]: PASS / HOLD
[HUMAN_OVERRIDE]: ACCEPTED / ACCEPTED_MANUAL / REJECTED / N/A
[REASON]:

Review (Phase 7):
[JUDGMENT]: 계속 / 종료 / 보류 / 피벗 / 중단
[HUMAN_OVERRIDE]: ACCEPTED / ACCEPTED_MANUAL / REJECTED / N/A
[REASON]:

Iteration (Phase 2):
[ITERATION_SCOPE]: DRAFT / NEED_INPUT
[REASON]:
```

**금지:**
- 태그 없이 일반 안내만 출력
- 선행조건 확인 없이 바로 구현/수정 시작
- 블록 필드 생략

**추가 강제 규칙 (2026-05-26):**
- 새 엔진/별도 모듈 요청이면 `SEPARATE_TRACK_EXECUTION` + `Phase 2` lock 없이 구현하지 않는다.
- `active_track`, `phase_lock`, `activation_gate_state`, `scope_source_of_truth`, `implementation_permission`가 비어 있으면 구현하지 않는다.
- `implementation_permission=docs_only`면 문서와 trace만 허용하고 코드 구현은 금지한다.
- `"1단계부터"`, `"처음부터"`, `"단계별로"` 요청이면 기존 구현 컨텍스트를 잇지 않고 `SEQUENTIAL_PHASE_REVIEW`로 다시 잠근다.

---

## Phase 워크플로우

```
Phase 0  Context 작성       → docs/00~04.md
Phase 1  Decision           → [DECISION]: GO / HOLD / KILL
Phase 2  Scope & MVP        → decision-lock.md
Phase 3  Architecture       → docs/07_architecture.md
Phase 4  Execution Gate     → [GATE]: OPEN
Phase 5  Task Breakdown     → tasks/task-list.md
Phase 6  Implementation     → 코드 구현
Phase 7  Execution Review   → [JUDGMENT]
Phase 8  Deployment         → 배포 완료
Post     GTM & Operations   → docs/marketing/, docs/business/
```

**선행조건 체크 (구현 전 필수):**
```
decision-lock.md 존재?       → 없으면 Phase 2 먼저
docs/07_architecture.md 존재? → 없으면 Phase 3 먼저
tasks/task-list.md 존재?     → 없으면 Phase 5 먼저
```

---

## 에이전트 실행 계약 (수 기준 SSOT: `docs/public/SKU_CATALOG_KO.md`)

각 에이전트는 아래 트리거 패턴에서 호출됩니다.  
Codex에서는 `@에이전트명` 형식으로 명시적 호출합니다.

### 사업 기획 (Pre-Phase 0)

**@expert-planner**
- 트리거: "사업 분석", "Target 분석", "Value 분석", "사업계획서", "수익 모델"
- 역할: 서비스 분석 → Target/Value → 수익 모델 → 경쟁 분석 → docs/business/ 생성
- 출력: `[EXPERT_PLANNER_RESULT]`

**@researcher**
- 트리거: "시장 조사", "경쟁 분석", "조사해줘"
- 역할: 시장/경쟁/기술 자료 조사. 결론 중심 요약(최대 5개)
- 출력: `[RESEARCH SUMMARY]`

### 의사결정 (Phase 1~4)

**@decision**
- 트리거: "이거 해도 돼?", "GO/HOLD/KILL", "판단해줘"
- 역할: 아이디어 실행 여부 GO/HOLD/KILL 판정
- 입력: docs/00~04.md 필수
- 출력: `[DECISION]: GO / HOLD / KILL`

**@mvp-builder**
- 트리거: "MVP 만들어줘", "스코프 정의해줘"
- 역할: docs/05~08.md 자동 생성
- 출력: `[MVP_BUILT]`

**@architecture**
- 트리거: "아키텍처 설계", "시스템 설계"
- 역할: docs/07_architecture.md 생성
- 출력: `[ARCHITECTURE_COMPLETE]`

**@execution-manager**
- 트리거: "Execution 진입", "decision-lock 확인"
- 역할: decision-lock.md 확인 후 OPEN/HOLD 판정
- 출력: `[GATE]: OPEN / HOLD`

**@pipeline-coordinator**
- 트리거: "Phase 전환", "다음 단계", "파이프라인 조율", "어느 단계야", "지금 어디까지 했어", "현황 알려줘"
- 역할: 현재 Phase 자동 판별 → 다음 Phase 진입 조건 검증 → 에이전트/커맨드 호출 지시 → docs/state/current-snapshot.md 자동 갱신
- 출력: `[PIPELINE_COORDINATOR]`

**@cost-guard**
- 트리거: "비용 확인", "토큰 사용량", "예산 초과", "API 비용"
- 역할: 실행 예정 에이전트 체인 예상 토큰/비용 추정 → 예산 초과 시 HOLD
- 출력: `[COST_CHECK]`, `[GATE]: PASS / HOLD`
- **자동 통합 (v3.1):**
  - `task-analysis-gate` Step 5에서 자동 호출 (구현 시작 전)
  - `execution-manager` Step 6에서 자동 호출 (Execution Gate 진입 전)
  - `pipeline-coordinator` S 등급 Phase 전환 시 자동 호출
  - `cost-guard-automation` Skill로 PreToolUse hook 자동 트리거
  - 누적 추적: `docs/state/cost-tracking.md`

**@incident-responder**
- 트리거: "배포 후 오류", "프로덕션 에러", "장애 대응", "핫픽스", "서비스 다운"
- 역할: 오류 메시지 분석 → 등급 분류 → 근본 원인 가설 → 즉시 조치 체크리스트 → 핫픽스 경로 제안
- 출력: `[INCIDENT_RESPONSE]`

### 설계 (Phase 3.5~5)

**@screen-designer**
- 트리거: "화면 설계", "와이어프레임", "UI 플로우", "화면 정의서", "페이지 구조"
- 역할: docs/02_user.md + docs/03_journey.md + docs/06_mvp.md 기반 화면 목록/구성요소/전환 플로우 명세 생성
- 출력: `[SCREEN_DESIGN]`, docs/screens/

**@api-designer**
- 트리거: "API 설계", "API 명세", "OpenAPI", "엔드포인트 설계", "REST 설계", "API 문서"
- 역할: docs/07_architecture.md 기반 엔드포인트 목록/요청응답 스키마/OpenAPI 3.0 YAML 생성
- 출력: `[API_DESIGN]`, docs/api/

**@db-designer**
- 트리거: "DB 설계", "데이터베이스 설계", "ERD", "스키마 설계", "테이블 설계", "마이그레이션"
- 역할: docs/07_architecture.md 기반 ERD/SQL DDL/Prisma 스키마/마이그레이션 전략 생성
- 출력: `[DB_DESIGN]`, docs/db/

### 개발 (Phase 5~7)

**@task-breakdown**
- 트리거: "Task 분해", "작업 나눠", "/task-breakdown"
- 역할: docs/07_architecture.md → tasks/task-list.md
- 출력: `[TASK_LIST_CREATED]`

**@implementation**
- 트리거: "Task #N 시작", "구현해", "/implement TASK-XX"
- 역할: 코드 구현 (파일 생성/수정)
- 출력: `[IMPLEMENTATION COMPLETE]`

**@implementation-orchestrator**
- 트리거: "구현 시작", "Implementation 준비"
- 역할: 구현 선행조건 확인 및 안내
- 출력: `[IMPLEMENTATION AGENT READY]`

**@execution-review**
- 트리거: "중간 점검", "3개 Task 완료", "계속할까"
- 역할: 계속/종료/보류/피벗/중단 판정
- 출력: `[JUDGMENT]`

### QA 파이프라인

**@testgen**
- 트리거: "테스트 생성", "TestGen", "구현 완료"
- 역할: Playwright/Jest/pytest 테스트 자동 생성
- 출력: `[TESTGEN_COMPLETE]`

**@healer**
- 트리거: "테스트 실패", "테스트 에러", "TEST EXECUTION FAILED"
- 역할: 실패 원인 분석 및 수정 제안
- 출력: `[HEALER_DIAGNOSIS]`

**@testops**
- 트리거: "테스트 결과 분석", "TestOps", "테스트 완료"
- 역할: 테스트 결과 집계, Flaky 감지, 트렌드 분석
- 출력: `[TESTOPS_REPORT]`

**@code-quality**
- 트리거: "코드 품질", "코드 리뷰", "/review"
- 역할: ESLint/TS/중복 검증. Critical/Warning/Suggestion 분류
- 출력: `[CODE_QUALITY_REPORT]`

**@ux-gate**
- 트리거: "UX 검증", "UI 검토", "/ux-gate"
- 역할: 문구/퍼널/접근성 종합 검증
- 출력: `[UX_GATE_RESULT]`

**@target-value-uiux-auditor**
- 트리거: "Target Value UIUX 평가", "타깃 가치 UI 평가", "현재 UI가 고객에게 맞나", "가시성 심미성 평가", "웹 앱 UX 적합성"
- 역할: docs의 Target/Persona/JTBD/Value 기준으로 현재 Web/App UIUX와 기능 적합성, 가시성, 심미성, 전환력, 신뢰감을 평가 → 개선 Task 도출
- 출력: `[TARGET_VALUE_UIUX_AUDIT]`

**@spec-implementation-verifier**
- 트리거: "문서 반영 검증", "Spec vs Implementation", "스펙 구현 검증", "문서대로 구현됐나", "설계 대비 실제 구현", "docs와 src 비교"
- 역할: docs/screens/api/business/marketing/tasks와 실제 src/app 구현을 비교해 Missing/Mismatch/Overbuilt/Incorrect/UX Gap을 찾고 수정 Task로 변환
- 출력: `[SPEC_IMPLEMENTATION_VERIFICATION]`

**@security-tester**
- 트리거: "보안 테스트", "Security Test", "권한 테스트", "앱 보안 감사", "OWASP", "IDOR", "API 보안", "출시 전 보안 감사"
- 역할: 플랫폼/프레임워크 비종속 애플리케이션 보안 감사. OWASP Top 10, OWASP API Security Top 10, Secret/API Key, 인증/인가, IDOR, Injection, 파일 업로드, 결제/크레딧, 배포 설정, AI 기능 보안을 출시 전 기준으로 검토
- 출력: `[SECURITY_TEST_RESULT]` with 전체 보안 판정 / P0~P3 취약점 표 / 개발자 수정 지시서 / 재검증 체크리스트 / Go-No-Go 기준

**@integration-tester**
- 트리거: "통합 테스트", "API 연동 확인"
- 역할: FE-BE 연동 시나리오 검증
- 출력: `[INTEGRATION_TEST_RESULT]`

**@performance-auditor**
- 트리거: "성능 점검", "배포 전 성능"
- 역할: LCP/TTI/번들 크기 점검. READY/HOLD 판정
- 출력: `[PERFORMANCE_AUDIT]`

### 마케팅/GTM

**@GTM-Strategist**
- 트리거: "마케팅 전략", "GTM", "유저 획득", "SEO", "런칭 계획"
- 역할: 배포 후 GTM 전략 수립 → docs/marketing/ 생성
- 출력: `[GTM_STRATEGY_RESULT]`

### 배포/운영

**@deployment**
- 트리거: "배포 안내", "배포 체크리스트", "/deploy"
- 역할: 배포 전 체크리스트 및 롤백 안내 (실행 안 함, 안내만)
- 출력: `[DEPLOYMENT CHECKLIST]`

**@pre-launch-final-auditor**
- 트리거: "최종 검토", "출시 가능 여부", "Go No-Go", "Pre Launch Audit", "출시 승인", "릴리즈 차단 요소", "런칭 전 마지막 점검"
- 역할: 사업/UX/기술/운영/데이터/마케팅 리스크와 Release Blocker를 통합 검토 → GO / CONDITIONAL_GO / NO_GO 판단
- 출력: `[PRE_LAUNCH_FINAL_AUDIT]`

**@deployment-secrets-auditor**
- 트리거: "시크릿 감사", "secrets audit", "배포 보안"
- 역할: CI/CD 및 배포 플랫폼 시크릿 감사
- 출력: `[DEPLOYMENT_SECRETS_AUDIT]`

**@secret-guard**
- 트리거: "커밋 전 점검", "시크릿 유출 확인"
- 역할: .env/token/secret 탐지 및 차단
- 출력: `[SECRET_GUARD_RESULT]`

**@devops-guard**
- 트리거: "환경 점검", "Docker 멈춤", "느려졌다"
- 역할: Cursor/Docker/Git/Node 상태 감시
- 출력: `[STATUS CHECK]`

### 개발 감사

**@dev-auditor**
- 트리거: "개발 분석", "코드 감사", "기술 부채", "배포 이슈 분석"
- 역할: 아키텍처 적합성/기술 부채/배포 파이프라인 종합 판정
- 출력: `[DEV_AUDIT_RESULT]`

**@task-analysis-gate**
- 트리거: "구현 시작", "구현해도 돼?", "TASK-XX 구현", "분석 완료?", "task gate"
- 역할: 구현 전 강제 게이트 — Task 존재 + 분석 완료 + 이전 테스트 통과 확인
- 출력: `[GATE]: OPEN | BLOCKED`
- 연동: tasks/task-list.md + docs/state/execution-context.md

**@code-analyzer**
- 트리거: "코드 분석", "구조 파악", "프로젝트 분석"
- 역할: 코드베이스 구조 파악, 변경 영향 분석
- 출력: `[CODE_ANALYSIS]`

**@codebase-onboarding**
- 트리거: "온보딩", "코드베이스 파악", "현황 분석"
- 역할: 구조/실행경로/리스크 빠른 파악
- 출력: `[ONBOARDING_REPORT]`

### 제품 진단 / 스택

**@product-diagnosis**
- 트리거: "우리 제품 어때", "제품 진단", "종합 진단", "전방위 분석", "서비스 현황 분석", "제품 건강도", "단계별로 분석해줘"
- 역할: Phase 0(사업)→Phase 3(설계)→Phase 6(개발)→Phase 7(UX/보안)→Phase 8(GTM) 전 레이어 종합 진단 + 취약 레이어 + 즉시 조치 TOP 3 제시
- 출력: `[PRODUCT_DIAGNOSIS]`, [BUSINESS_HEALTH], [DESIGN_HEALTH], [DEV_HEALTH], [QA_HEALTH], [GTM_HEALTH], [OVERALL]

**@stack-advisor**
- 트리거: "기술 스택 추천", "프레임워크 선택", "어떤 기술 써야 해", "스택 결정"
- 역할: MVP 요구사항 기반 프론트엔드/백엔드/DB/인프라 스택 추천 + 보일러플레이트 구조 제공
- 출력: `[STACK_RECOMMENDATION]`

### 멀티영역 라우팅 (D-50 PROMOTION)

> engine PROMOTION 흡수 자산. Claude Code 라우터 룰 #34와 정합 (2026-06-03 IDE 동기화).

**@project-router**
- 트리거: "지침에 따라 [프로젝트X] 진행해", "[프로젝트X] 전체 분석", "[프로젝트X] 통합 진행"
- 역할: 사업/개발 영역 자동 분류 + 영역별 chain 자동 호출 (마스터 진입점)
- 출력: `[PROJECT_ROUTER]`

### 웹 크롤링 및 데이터 분석 파이프라인 (Phase 6 / 7)

**@crawler-analyst-agent**
- 트리거: "웹 크롤링 분석", "크롤러 생성", "타겟 사이트 분석", "크롤링 파이프라인", "리포트 대시보드 자동화"
- 역할: 타겟 사이트 구조 분석 → 스캐폴딩 스크립트 실행으로 뼈대 코드 구축 → 타겟 맞춤형 scraper.py 수정 및 실행 → run_pipeline.py 제어를 통해 Pre/Post Hook 가동 및 EDA, Excel 대시보드, Word/PPTX 리포팅 자동 연동 및 검증
- 출력: `[CRAWLER_ANALYSIS_PIPELINE_COMPLETE]`

### 유지보수/운영 자동화

**@legacy-cleaner**
- 트리거: "레거시 정리", "기술 부채", "deprecated 코드", "사용 안 하는 코드", "코드 정리"
- 역할: 미사용 코드/파일/의존성 식별 → 위험도 분류 → 안전한 제거 로드맵 생성
- 출력: `[LEGACY_ANALYSIS]`

**@release-manager**
- 트리거: "버전 올려", "릴리즈 준비", "changelog", "릴리즈 노트", "semantic versioning"
- 역할: git log 분석 → MAJOR/MINOR/PATCH 버전 판정 → CHANGELOG.md + 릴리즈 노트 생성
- 출력: `[RELEASE_MANAGER]`

**@data-pipeline-designer**
- 트리거: "데이터 파이프라인", "데이터 수집", "ETL", "데이터 웨어하우스", "로그 수집", "이벤트 파이프라인"
- 역할: 원천 데이터 수집 → ETL 변환 → 저장/서빙 레이어까지 전체 데이터 흐름 아키텍처 설계
- 출력: `[DATA_PIPELINE_DESIGN]`, docs/data/

**@cicd-designer**
- 트리거: "CI/CD 설계", "GitHub Actions", "배포 자동화", "파이프라인 설계", "배포 워크플로우"
- 역할: 아키텍처 기반 GitHub Actions 워크플로우 설계 → 환경별(dev/staging/prod) 파이프라인 생성
- 출력: `[CICD_DESIGN]`, .github/workflows/, docs/cicd/

### 도구 에이전트

**@git-helper**
- 트리거: "커밋", "브랜치", "머지", "Git"
- 역할: 커밋 메시지 생성, 브랜치 관리, 충돌 해결 (명령어 안내만)
- 출력: `[COMMIT MESSAGE]`, `[BRANCH COMMAND]`

**@writer**
- 트리거: "문서 정리", "톤 변환", "재작성"
- 역할: 기획서/투자자료 톤으로 재작성
- 출력: 변환된 문서

**@business-visualization-architect**
- 트리거: "사업 설명 시각화", "플로우차트", "엔진 구조도", "Mermaid", "IR 구조도", "서비스 구조도", "데이터 흐름도", "UI 구조도"
- 역할: 현재 기획/구현 기반 사업 설명용 플로우차트, 고객 여정 구조도, 엔진/AI 구조도, 데이터 흐름도, Web/App UI 구조도, 기능-가치-수익 연결도 생성
- 출력: `[BUSINESS_VISUALIZATION]`

**@ide-router-verifier**
- 트리거: "IDE 검증", "라우터 정합성", "IDE별 확인"
- 역할: 5개 IDE 환경의 라우터 파일 정합성 비교
- 출력: `[IDE_ROUTER_RESULT]`

**@claude-code-integration**
- 트리거: "파일 동기화", "다음 실행 단계"
- 역할: Claude Code와 Cursor 간 파일/단계 동기화 점검
- 출력: `[INTEGRATION CHECK]`

**@memory-manager**
- 트리거: "기억해줘", "이전 작업", "컨텍스트 복원", "이어서 진행"
- 역할: 프로젝트 컨텍스트 자동 저장/복원 (세션 간 이어받기)
- 산출물: `.claude/projects/[project-name]/memory/`
- 출력: `[MEMORY_RESTORED]`

**@agent-log-auditor**
- 트리거: "에이전트 성능 분석", "라우터 태그 커버리지", "에이전트 로그 분석", "응답 품질 점검"
- 역할: 파일 기반 에이전트 실행 로그 분석 (태그 커버리지, 오류 패턴, Phase 분포)
- 출력: `[AGENT_LOG_AUDIT]`

**@pattern-extractor**
- 트리거: "반복 패턴 분석", "자동화 후보", "스킬로 만들 수 있는 것", "채널 패턴 정리", "어떤 게 에이전트화 가능해"
- 역할: Cursor/Claude/Codex 채널 로그 반복 패턴 클러스터링 → Skill/Agent 자동화 후보 도출 → [AGENT/SKILL DESIGN] 초안 생성
- 출력: `[PATTERN_ANALYSIS]`, docs/analysis-results/automation-candidates-YYYYMMDD.json

**@agent-evaluator**
- 트리거: "에이전트 출력 검증", "출력 계약 회귀 테스트", "agent contract check"
- 역할: 각 에이전트의 출력 포맷(태그 블록, 필드) 완전성을 정적 분석으로 검증
- 출력: `[AGENT_EVALUATOR]: PASS / PARTIAL / FAIL`

**@verifiable-test-runner**
- 트리거: "verifiable test", "정량 검증", "verify", "Hybrid Norm"
- 역할: 자산별 정량 grep·단위 검증·출력 형식 검증 (agent-evaluator Rubric과 보완, 2축 동시 평가)
- 출력: `[VERIFIABLE_RESULT]`, eval_YYYY-MM.md

**@asset-comparison-gate**
- 트리거: "새 에이전트", "스킬 추가", "기존 에이전트와 비교", "기존 스킬과 비교", "자산 비교", "asset comparison"
- 역할: 신규 에이전트/스킬/자동화 자산 생성 전 Builder·Enterprise 기존 자산과 비교해 REUSE/EXTEND/MERGE_REVIEW/CREATE 판정
- 실행: `python3 scripts/compare-agent-skill-assets.py --query "[요청 기능 요약]" --top 10`
- 출력: `[ASSET_COMPARISON_GATE]`, `[VERDICT]: REUSE / EXTEND / MERGE_REVIEW / CREATE`

**@clear-safe**
- 트리거: "clear 해도 돼", "컨텍스트 정리", "세션 정리", "Task 끝나면 clear", "[TASK_COMPLETE]", "[JUDGMENT]: 종료"
- 역할: `/clear` 전 재진입 체크포인트를 생성하고 clear 가능 여부를 READY/WARN/HOLD로 판정
- 실행: `python3 scripts/clear-safe.py --reason "manual"`
- 출력: `[CLEAR_SAFE]`, `[VERDICT]: READY / WARN / HOLD`

**@data-analyst**
- 트리거: "데이터 분석해줘", "CSV 분석", "JSONL 분석", "지표 분석", "통계 요약"
- 역할: 구조화 데이터(CSV/JSONL/JSON/SQL) 분석 → 통계·트렌드·이상값 도출
- 출력: `[DATA_ANALYSIS]` with 통계 요약 + TOP 3 인사이트

**@cs-support-agent**
- 트리거: "CS 티켓 처리해줘", "고객 문의 분류해줘", "지원 요청 처리"
- 역할: CS 티켓 분류(BUG/FEATURE/HOW_TO/BILLING/기타) + 응답 초안 생성 + 에스컬레이션
- 출력: `[CS_TICKET]: [분류]` with 표준 응답 초안 + 에스컬레이션 경로

**@architecture-drift-detector**
- 트리거: "아키텍처 점검해줘", "설계 일치도 확인", "구조 검증", "설계 괴리 감지"
- 역할: docs/07_architecture.md와 실제 src/ 코드 정합성 검증
- 출력: `[ARCHITECTURE_DRIFT_DETECTOR]` with 구조/기술스택/의존성/데이터흐름 분석

**@pr-reviewer**
- 트리거: "PR 검토해줘", "PR 리뷰", "GitHub PR #[N]"
- 역할: GitHub PR diff 자동 분석 → 위험 라인/코드냄새/리뷰 포인트 선별
- 출력: `[PR_REVIEWER]` with 변경범위/위험라인/테스트커버리지 분석

**@ops-issue-triage**
- 트리거: "운영 이슈 정리해줘", "VOC 분석", "CS 우선순위", "이탈 포인트", "반복 오류", "사용자 불편 정리"
- 역할: VOC/CS 문의/이탈 포인트/장애 내역 수집 → 사용자 영향도·재발 가능성 기준 P0~Drop 분류 → 운영 실행 계획 생성
- 출력: `[OPS_ISSUE_TRIAGE]` with 이슈 목록/점수표/P0~Drop 분류/실행 계획

**@event-schema-designer**
- 트리거: "이벤트 설계해줘", "트래킹 설계", "데이터 설계", "퍼널 이벤트", "GA4 설계", "CRM 연동", "대시보드 설계", "이벤트 정의"
- 역할: 서비스 사용자 행동 이벤트 스키마 설계 → AARRR 퍼널 이벤트 맵 → CRM 연동 구조 → 대시보드 초안 → 개발자 구현 가이드 생성
- 출력: `[EVENT_SCHEMA_DESIGN]` with 이벤트 정의표/퍼널맵/CRM연동/대시보드 설계

**@business-impact-prioritizer**
- 트리거: "우선순위 재정렬해줘", "Task 우선순위", "사업 임팩트", "뭐부터 해야 해", "개발 우선순위", "스프린트 계획", "이거 먼저야 저거 먼저야", "분석 기반 Task", "Gap 기반 백로그"
- 역할: 현재 개발본 기준 남은 Task 또는 기존 분석 산출물의 Gap/Risk/성과 항목을 근거 기반 Task Inventory로 변환 → 매출/전환율/유지율 기준 점수화 → P0/P1/P2/P3/Drop 분류 → Sprint Plan 생성
- 출력: `[BUSINESS_IMPACT_PRIORITY]` with 임팩트 점수표/우선순위 매트릭스/갭 분석/로드맵

---

### Growth (Phase 10)

**@cohort-analyst**
- 트리거: "코호트 분석", "리텐션 분석", "D1 D7 D30", "Churn 분석", "이탈 패턴", "LTV 분석", "유저 유지율"
- 역할: D1/D7/D30 리텐션 커브 분석 → 코호트별 이탈 패턴 → Churn 원인 분류 → LTV 추정 → 리텐션 개선 우선순위 도출
- 출력: `[COHORT_ANALYSIS]` with 리텐션 커브/코호트 세그먼트/Churn 분석/LTV 추정

**@feature-flag-manager**
- 트리거: "Feature Flag", "피처 플래그", "Canary 배포", "점진적 롤아웃", "A/B 테스트 셋업", "Kill Switch", "실험 관리"
- 역할: Feature Flag 명세 설계 → 점진적 롤아웃 계획 → A/B 테스트 실험 설계 → Flag 생명주기 관리
- 출력: `[FEATURE_FLAG_DESIGN]` with Flag 명세/롤아웃 계획/실험 설계/코드 패턴

---

### 분석 (Phase 12)

**@qualitative-analyst**
- 트리거: "인터뷰 분석", "VOC 분석", "NPS 해석", "사용자 피드백 정리", "정성 데이터", "고객 목소리"
- 역할: 사용자 인터뷰/VOC/NPS/CS 텍스트에서 주제 클러스터링 → Pain Point/Unmet Need/Delight 추출 → 가설 및 다음 액션 도출
- 출력: `[QUALITATIVE_ANALYSIS]` with 오픈코딩/감정분석/기회영역/가설

**@hypothesis-mapper**
- 트리거: "가설 정리", "사업 가설", "제품 가설", "검증 가설", "우리가 믿고 있는 것", "현재 개발본 기준 가설", "가설 우선순위"
- 역할: 현재 개발본과 사업/서비스 문서를 기반으로 고객/문제/가치제안/UX/기능/사업/운영 데이터 가설을 정리하고 H1/H2/H3/Drop 검증 우선순위와 실험 액션 도출
- 출력: `[HYPOTHESIS_MAP]`

---

### 인프라 / 비용 (Phase 7 / 11)

**@iac-designer**
- 트리거: "IaC", "Terraform", "Pulumi", "AWS CDK", "인프라 코드", "클라우드 인프라 설계", "환경 분리 코드"
- 역할: 아키텍처 기반 Terraform/Pulumi/AWS CDK 모듈 구조 설계 → 코드 초안 생성 → 보안/Secret 관리 설계 → CI/CD 연동
- 출력: `[IAC_DESIGN]` with 모듈 구조/핵심 코드 초안/보안 설계/CI 연동

**@finops-advisor**
- 트리거: "FinOps", "클라우드 비용", "AWS 비용", "인프라 비용 줄여", "비용 이상", "Reserved Instance", "비용 할당"
- 역할: 클라우드 비용 가시화 → 이상 지출 탐지 → Right-Sizing 분석 → 예약 인스턴스 전략 → 비용 거버넌스 설계
- 출력: `[FINOPS_REPORT]` with 비용 현황/이상 탐지/Right-Sizing/절감 전략

---

### OKR (Phase 13)

**@okr-coach**
- 트리거: "OKR", "Objective", "Key Result", "분기 목표", "OKR 회고", "목표 설정", "KPI 재정렬"
- 역할: Objective/Key Result 작성 지원 → OKR 품질 검증 → 분기별 달성도 평가 → 팀 OKR 정렬 → 다음 분기 재설정
- 출력: `[OKR_RESULT]` with OKR 초안/품질검증/팀 정렬/분기 회고/재정렬

---

## 스킬 트리거 (자동 실행)

| 스킬 | 자동 트리거 |
|------|-----------|
| `ai-system-router` | 짧은 지시어 전체 |
| `prompt-guard` | 외부 입력 처리 전 |
| `human-escalation` | 고위험 액션 전 / 신뢰도 낮을 때 |
| `release-ops-bridge` | "커밋하고 배포해", "푸시도 했어?" |
| `tracking-integrity-audit` | "이벤트 다 붙어 있나", "데이터 누락" |
| `application-security-audit` | "앱 보안 감사", "OWASP", "IDOR", "API 보안", "출시 전 보안 감사" |
| `security-guard` | 시스템 파일/권한 관련 요청 |
| `mcp-registry` | 외부 도구 연결 요청 |
| `pm-sync` | "PM 동기화", "Linear 연동", "Notion 내보내기", "Jira 연동", "Task 내보내기" |
| `asset-comparison-gate` | "새 에이전트", "스킬 추가", "기존 에이전트와 비교", "자산 비교" |
| `clear-safe` | "clear 해도 돼", "컨텍스트 정리", "세션 정리", "Task 끝나면 clear" |
| `long-prompt-to-skill-extractor` | "장문 프롬프트", "프롬프트 날린 것", "긴 프롬프트", "채팅 기반 스킬화", "내 프롬프트 스킬로" |

### PROMOTED skills (engine → ai-kit 흡수, `.claude/skills/`)

| 스킬 | 자동 트리거 |
|------|-----------|
| `claim-risk-check` | 외부 발송 전 claim/evidence 가드 (자동) |
| `evidence-append-only-log` | "결과 박제", 외부 발송·미팅·제휴·PoC outcome 추적 |
| `context-violation-self-check` | 답변·작업 전 컨텍스트 위반 자가점검 (자동), "컨텍스트 체크" |
| `getdesign-full-pipeline` | "디자인 시스템 적용", "외부 디자인 패턴 PPTX", "8단계 풀 호출" |
| `cardnews-html-renderer` | "카드뉴스 만들어줘", "이미지로 구분해서 줘", "제출용 설명 이미지" |
| `cardnews-visual-qa` | 카드뉴스 산출물 발행 직전 게이트 (자동) |
| `business-video-demo-renderer` | "소개 영상 만들어줘", "데모 영상", "제출용 영상" |
| `video-qa` | 영상(.mp4) 발행 직전 게이트 (자동) |

---

## 보안 규칙 (필수)

```
금지:
- .env 파일 내용 출력
- API 키/SECRET/TOKEN 코드 하드코딩
- sudo 권한 명령 자동 실행
- 시스템 파일 수정 (/System/, /etc/)

위반 감지 시:
[SECURITY_VIOLATION]: [위반 유형]
[REASON]: [내용]
[IMMEDIATE_ACTION]: [조치]
```

---

**버전:** AI-SYSTEM v3  
**정본 SSOT:** `prompts/00_router_v3.md`

---

## 콘텐츠 운영 시스템 (Content OS)

본 섹션은 v1.0(2026-04-24)에 추가된 Content OS 부트스트랩 에이전트입니다.
상세 패턴 정본은 `docs/content-os-pattern.md`.

### Content OS — Bootstrap Chain

**@bp-analyzer**
- 트리거: "사업계획서 분석", "IR 파싱", "정체성 추출", "콘텐츠 OS 부트스트랩"
- 역할: PDF/DOCX 사업계획서에서 정체성·페르소나·숫자 화이트리스트·리스크 추출
- 입력: BP 파일
- 출력: `[BP_EXTRACT]`, `docs/bp_extract.md`

### Content OS — Creation Pipeline

**@legal-reviewer**
- 트리거: "법무 검토", "동의서 확인", "개인정보 체크"
- 역할: 콘텐츠의 개인정보, 실명, 국적, 규제 민감 영역을 탐지하고 동의/익명화/법무 자문 필요성을 판정
- 출력: `[LEGAL_CHECK]`

### 산출물 구조 (참고)

이 패턴을 적용하면 프로젝트별로 아래 형태의 산출물이 생성됩니다:
- 전략 가이드: `<project>/00_strategy_<name>.docx`
- 설계 명세 v1: `<project>/00_strategy/content_system_design_v1.md`
- Decision v1: `<project>/decisions/content-os-v1.md`
