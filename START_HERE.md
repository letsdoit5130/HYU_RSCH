# AI-Developer-KIT — START HERE

> 설치 직후 자동으로 열리는 첫 화면입니다. 3분 안에 첫 산출물까지 갑니다.

## 0. 개인정보 경계 (먼저 안심하세요)
**고객의 prompt, code, file, document, business idea는 Ain 서버로 전송되지 않습니다.**
Ain은 라이선스 확인, 업데이트 확인, opt-in 익명 제품 신호, 선택형 feedback/diagnostics만 처리합니다.
키트는 고객의 AI 개발 도구(Claude Code / Codex / Antigravity / Cursor) **안에서 로컬로** 실행됩니다. (상세: `docs/security/PRIVACY_BOUNDARY_ONE_PAGER.md`)

## 1. 첫 메시지 (어느 팩이든 공통)
이 KIT는 **여러분의 작업 폴더 안에서** 동작합니다. 이미 구현 중인 레포지토리·프로젝트 폴더가 있으면 그 폴더에서, 없으면 이 폴더에서 시작하세요.
쓰시는 AI 개발 도구(Claude Code · Codex · Antigravity · Cursor)에서 그 폴더를 열고, 첫 메시지로:
```
지침에 따라 진행해
```
→ 라우터가 현재 상태를 감지해 다음 단계로 안내합니다.

## 2. 목적별 첫 사용 command
| 목적 | 첫 command | 산출물 |
|---|---|---|
| 이걸 만들까 말까 판단 | `/decision` | GO/HOLD/KILL + decision-lock.md (= 첫 가치) |
| 아이디어 → 배포 전 과정 | `/idea-to-deploy` | Phase 0~8 파이프라인 |
| 설계 → 작업 분해 | `/task-breakdown` | tasks/task-list.md |
| 코드 품질·리뷰 | `/review` | 코드 리뷰 리포트 |
| 제품 종합 진단 | `@product-diagnosis` | 취약 레이어 + 즉시조치 TOP3 |

> 각 유료팩(Builder Pro / Enterprise)은 해당 폴더의 `START_HERE.md`에 팩 전용 첫 command가 있습니다.
> 마케팅·GTM은 별도 제품 **AI-MARKETING**, 정부지원·RFP·자금은 별도 제품 **BIDS**에서 제공합니다 (이 키트는 Phase 0~8 전용).

## 3. 상태 점검·업데이트 (CLI)
```
npx ai-system doctor        # 설치/활성화/런타임/설정 health 진단
npx ai-system update        # 최신 버전 확인
npx ai-system diagnostics   # 익명 진단 리포트(내용 불포함)
npx ai-system feedback "…"  # 로컬 피드백 초안(자동 전송 없음)
```

## 4. 온보딩 가이드 (역할별)
- 비개발자: `docs/public/LEARNER_START_HERE_KO.md`
- 개발자: `QUICK_START.md`
- PM/Codex: `docs/public/CODEX_START_HERE_KO.md`
