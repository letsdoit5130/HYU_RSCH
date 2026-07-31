---
name: trade-gen4-un-auto-mining
description: trade-gen2.2-un-partner-deep-mining을 완전 자동화한 버전입니다. GitHub Actions에서 Gemini API(Google Search grounding)를 직접 호출해 사람/AI 세션 개입 없이 실제 파트너를 찾아 Verified_Partners 시트에 병합합니다. "완전 자동화", "컴퓨터 꺼도 계속 조사", "API로 자동 리서치" 요청 시 활성화됩니다.
---

# 🤖 Trade Gen4 — 완전 자동 딥마이닝 (Gemini API + Search Grounding)

`trade-gen2.2-un-partner-deep-mining`은 Claude Code 같은 대화형 AI 세션이 WebSearch/WebFetch로
직접 조사하는 방식이라 **세션(컴퓨터)이 꺼지면 멈춘다.** 이 스킬은 그 한계를 없애기 위해
GitHub Actions에서 Gemini API를 직접 호출해, 사람 개입·컴퓨터 전원과 무관하게 클라우드에서
완전 자동으로 실제 회사를 검색·검증·병합한다.

---

## ⚠️ 시작 전 필수 설정 — `GEMINI_API_KEY`

이 스킬은 **API 키 없이는 작동하지 않습니다** (당연히, 아무도 몰래 대신 검색해주지 않습니다).

1. https://aistudio.google.com/apikey 에서 Gemini API 키 발급
2. GitHub 저장소 → **Settings → Secrets and variables → Actions → New repository secret**
3. Name: `GEMINI_API_KEY`, Value: 발급받은 키 → **Add secret**

이 secret이 없으면 워크플로우가 `[ERROR]: GEMINI_API_KEY 환경변수` 메시지와 함께 즉시
실패합니다(크래시가 아니라 명확한 에러 — 계속 실패해도 원인을 바로 알 수 있음).

---

## 💰 비용에 대해

이건 **API 종량제**입니다. 대화형 세션과 달리 실행할 때마다 실제 비용이 발생합니다.
- 기본값은 **1회 실행에 신규 후보국 상위 3개국만** 조사합니다(`--top_n 3`).
- 기본 스케줄은 **하루 1회**입니다 (기존 국가 우선순위 갱신 cron의 4회보다 훨씬 낮은 빈도).
- `--top_n`을 늘리거나 스케줄을 더 자주 돌리면 비용도 비례해서 늘어납니다.

---

## ⚠️ 무결성 규칙 (trade-gen2.2와 동일)

1. Gemini에게 시스템 프롬프트로 "실제 검색 결과만, 출처 URL 필수, 불확실하면 빈칸"을 강제한다.
2. 응답에서 `source_url`이 없거나 `http`로 시작하지 않는 레코드는 **자동 거부**된다
   (`merge_research_findings.py`를 그대로 재사용 — 규칙이 두 곳에 따로 존재하지 않음).
3. Gemini의 Google Search grounding 메타데이터(실제 인용 URL)를 감사 로그(`{slug}_auto_mining_log.jsonl`)에
   원문 응답과 함께 남긴다 — 나중에 사람이 "이게 진짜 검색 결과였는지" 재검토할 수 있게.

---

## 🛠️ 실행 방법

```bash
export GEMINI_API_KEY=...
uv run python .agents/skills/trade-gen4-un-auto-mining/scripts/autonomous_deep_mining.py \
  --item "<품목명>" \
  --output_dir <프로젝트 폴더> \
  --item_slug <slug> \
  --top_n 3
```

GitHub Actions에서는 `.github/workflows/auto_deep_mining.yml`이 하루 1회 자동 실행하고,
`workflow_dispatch`로 수동 실행도 가능합니다(`top_n` 입력 파라미터 지정 가능).

---

## 🔁 다른 스킬과의 관계

| | trade-gen2.2 (대화형) | trade-gen4 (완전 자동) |
|---|---|---|
| 실행 주체 | Claude/Gemini 등 대화형 세션 | GitHub Actions + Gemini API |
| 컴퓨터 꺼지면 | 즉시 중단 | 계속 실행됨 |
| 비용 | 세션 사용 시간에 포함 | 실행마다 API 종량 과금 |
| 결과 저장 위치 | 동일 (`Verified_Partners` 시트) | 동일 (`Verified_Partners` 시트) |
| 병합 로직 | `merge_research_findings.py` | 동일 스크립트 재사용 |

두 스킬은 같은 `{slug}_buyers_leads.xlsx` 파일의 같은 시트에 누적되므로, 하나가 찾은 결과를
다른 하나가 지우지 않습니다.
